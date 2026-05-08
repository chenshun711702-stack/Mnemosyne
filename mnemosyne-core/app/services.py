import os
import base64
import chromadb
import tempfile
import whisper
import threading
from chromadb.utils import embedding_functions
from openai import OpenAI, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from datetime import datetime
from typing import List, Optional
from PIL import Image
from io import BytesIO
from sentence_transformers import SentenceTransformer
from .interfaces import IMemoryStorage, ILLMEngine
from .schemas import MemoryEntry, MemoryResponse

class CLIPEngine:
    _model = None
    _lock = threading.Lock()

    def __init__(self):
        # Model is lazy-loaded on first use
        pass

    @property
    def model(self):
        if CLIPEngine._model is None:
            with CLIPEngine._lock:
                if CLIPEngine._model is None:
                    print(f"[{datetime.now()}] Loading CLIP model (clip-ViT-B-32)...")
                    CLIPEngine._model = SentenceTransformer('clip-ViT-B-32')
        return CLIPEngine._model

    def get_text_embedding(self, text: str):
        return self.model.encode(text).tolist()

    def get_image_embedding(self, image: Image.Image):
        return self.model.encode(image).tolist()

class ChromaStorage(IMemoryStorage):
    def __init__(self, path: str):
        self.client = chromadb.PersistentClient(path=path)
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="memories_v2", 
            embedding_function=self.ef
        )
        self.clip = CLIPEngine()

    def add_memory(self, entry: MemoryEntry, encryptor=None) -> str:
        entry_id = f"mem_{int(datetime.now().timestamp() * 1000)}"
        clean_metadata = {k: v for k, v in entry.metadata.model_dump().items() if v is not None}
        content_to_store = entry.content
        embedding = self.clip.get_text_embedding(entry.content)

        if encryptor:
            clean_metadata["is_encrypted"] = True
            content_to_store = encryptor.encrypt(entry.content)
            
        self.collection.add(
            documents=[content_to_store],
            embeddings=[embedding],
            metadatas=[clean_metadata],
            ids=[entry_id]
        )
        return entry_id

    def add_image_memory(self, image_bytes: bytes, metadata: dict, encryptor=None) -> str:
        entry_id = f"img_{int(datetime.now().timestamp() * 1000)}"
        image = Image.open(BytesIO(image_bytes))
        embedding = self.clip.get_image_embedding(image)
        base64_img = base64.b64encode(image_bytes).decode('utf-8')
        
        metadata["is_image"] = True
        metadata["timestamp"] = datetime.now().isoformat()
        
        if encryptor:
            metadata["is_encrypted"] = True
            base64_img = encryptor.encrypt(base64_img)

        self.collection.add(
            documents=[base64_img],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[entry_id]
        )
        return entry_id

    def search_memories(self, query: str, n_results: int, encryptor=None):
        query_embedding = self.clip.get_text_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_embedding], 
            n_results=n_results
        )
        
        responses = []
        for i in range(len(results['ids'][0])):
            content = results['documents'][0][i]
            metadata = results['metadatas'][0][i]
            is_image = metadata.get("is_image", False)
            
            if encryptor and metadata.get("is_encrypted"):
                content = encryptor.decrypt(content)
            
            responses.append(MemoryResponse(
                id=results['ids'][0][i],
                content="[Visual Memory]" if is_image else content,
                metadata=metadata,
                distance=results['distances'][0][i],
                base64_content=content if is_image else None
            ))
        return responses

    def list_memories(self, limit: int = 10, encryptor=None) -> List[MemoryResponse]:
        results = self.collection.get(limit=limit)
        responses = []
        for i in range(len(results['ids'])):
            content = results['documents'][i]
            metadata = results['metadatas'][i]
            is_image = metadata.get("is_image", False)

            if encryptor and metadata.get("is_encrypted"):
                content = encryptor.decrypt(content)

            responses.append(MemoryResponse(
                id=results['ids'][i],
                content="[Visual Memory]" if is_image else content,
                metadata=metadata,
                base64_content=content if is_image else None
            ))
        
        responses.sort(key=lambda x: x.id, reverse=True)
        return responses

    def delete_memory(self, memory_id: str) -> bool:
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False

class OpenAIEngine(ILLMEngine):
    _whisper_model = None
    _lock = threading.Lock()

    def __init__(self, api_key: str, base_url: str = None):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1"
        ) if api_key else None

    @property
    def whisper_model(self):
        if OpenAIEngine._whisper_model is None:
            with OpenAIEngine._lock:
                if OpenAIEngine._whisper_model is None:
                    print(f"[{datetime.now()}] Loading Whisper model (small)...")
                    try:
                        OpenAIEngine._whisper_model = whisper.load_model("small")
                    except Exception:
                        print(f"[{datetime.now()}] Failed to load Whisper Small, falling back to Base.")
                        OpenAIEngine._whisper_model = whisper.load_model("base")
        return OpenAIEngine._whisper_model

    def analyze_sentiment(self, text: str) -> str:
        if not self.client:
            return "Neutral"
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "system", "content": "You are a sentiment analyzer. Respond with only one word: Positive, Negative, or Neutral."},
                          {"role": "user", "content": text}]
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "Neutral"

    def transcribe_audio(self, audio_bytes: bytes) -> str:
        with open("whisper_debug.log", "a") as f:
            f.write(f"\n[{datetime.now()}] Transcription request received. Bytes: {len(audio_bytes)}")
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        try:
            result = self.whisper_model.transcribe(
                tmp_file_path,
                initial_prompt="This is a personal digital memory archive named Mnemosyne. 这是一个个人数字记忆库。",
                fp16=False 
            )
            transcript = result["text"].strip()
            return transcript
        except Exception as e:
            return f"[Error: Local transcription failed: {str(e)}]"
        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    def generate_response(self, query: str, context: list) -> str:
        context_str = "\n".join([f"- {doc}" for doc in context])
        
        if not self.client:
            return f"本地模式: 以下是与您的查询相关的记忆：\n{context_str}"
        
        prompt = f"基于以下记忆内容回答用户：\n{context_str}\n\n问题：{query}"
        
        @retry(
            stop=stop_after_attempt(2),
            wait=wait_exponential(multiplier=1, min=2, max=6),
            retry=retry_if_exception_type(RateLimitError),
            reraise=True
        )
        def _call_llm():
            return self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}]
            )

        try:
            response = _call_llm()
            return response.choices[0].message.content
        except Exception as e:
            # Resilient Fallback: If API fails (balance/network), don't crash, provide local context
            print(f"[{datetime.now()}] LLM API failed: {str(e)}. Falling back to local context synthesis.")
            return f"（AI 接口暂不可用，已自动切换至本地摘要模式）\n我为您找到了以下相关记忆，它们可能包含您需要的答案：\n\n{context_str}"
