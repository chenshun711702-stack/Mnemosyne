import os
import base64
import chromadb
import tempfile
import whisper
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
    def __init__(self):
        # Local CLIP model - downloads on first run
        self.model = SentenceTransformer('clip-ViT-B-32')

    def get_text_embedding(self, text: str):
        return self.model.encode(text).tolist()

    def get_image_embedding(self, image: Image.Image):
        return self.model.encode(image).tolist()

class ChromaStorage(IMemoryStorage):
    def __init__(self, path: str):
        self.client = chromadb.PersistentClient(path=path)
        # Default text EF for standard text ingestion
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
        # Use CLIP for cross-modal search
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
        
        # 1. Generate CLIP embedding
        embedding = self.clip.get_image_embedding(image)
        
        # 2. Store as base64 in document
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
        # Use CLIP text embedding for query
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
        
        # Sort by ID descending (newest first)
        responses.sort(key=lambda x: x.id, reverse=True)
        return responses

    def delete_memory(self, memory_id: str) -> bool:
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False

class OpenAIEngine(ILLMEngine):
    def __init__(self, api_key: str, base_url: str = None):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1"
        ) if api_key else None
        try:
            # Try loading small model for better accuracy
            self.whisper_model = whisper.load_model("small")
        except Exception:
            # Fallback to base if small fails to load
            self.whisper_model = whisper.load_model("base")

    def analyze_sentiment(self, text: str) -> str:
        """Analyzes sentiment using GPT-4o-mini."""
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
        """Transcribes audio using local Whisper model with contextual prompting and language detection."""
        with open("whisper_debug.log", "a") as f:
            f.write(f"\n[{datetime.now()}] Transcription started. Bytes: {len(audio_bytes)}")
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        try:
            # initial_prompt helps with the context of the project
            # we don't force 'zh' so it can handle English too
            result = self.whisper_model.transcribe(
                tmp_file_path,
                initial_prompt="This is a personal digital memory archive named Mnemosyne. 这是一个个人数字记忆库，正在记录生活点滴。",
                fp16=False 
            )
            transcript = result["text"].strip()
            with open("whisper_debug.log", "a") as f:
                f.write(f"\n[{datetime.now()}] Transcription success: {transcript[:50]}...")
            return transcript
        except Exception as e:
            with open("whisper_debug.log", "a") as f:
                f.write(f"\n[{datetime.now()}] Transcription error: {str(e)}")
            return f"[Error: Local transcription failed: {str(e)}]"
        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    def generate_response(self, query: str, context: list) -> str:
        context_str = "\n".join([f"- {doc}" for doc in context])
        
        if not self.client:
            return f"本地模式: 我为您找到了以下相关记忆：\n{context_str}"
        
        prompt = f"基于以下记忆内容回答用户：\n{context_str}\n\n问题：{query}"
        
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type(RateLimitError),
            reraise=True
        )
        def _call_openai():
            return self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}]
            )

        try:
            response = _call_openai()
            return response.choices[0].message.content
        except RateLimitError:
            return f"AI 接口请求过于频繁。检索到的背景：\n{context_str}"
        except Exception as e:
            return f"AI 接口调用失败: {str(e)}。检索到的背景：\n{context_str}"
