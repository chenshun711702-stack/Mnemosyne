import os
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from datetime import datetime
from .interfaces import IMemoryStorage, ILLMEngine
from .schemas import MemoryEntry, MemoryResponse

class ChromaStorage(IMemoryStorage):
    def __init__(self, path: str):
        self.client = chromadb.PersistentClient(path=path)
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="memories", 
            embedding_function=self.ef
        )

    def add_memory(self, entry: MemoryEntry) -> str:
        entry_id = f"mem_{int(datetime.now().timestamp() * 1000)}"
        # Filter out None values because ChromaDB metadata doesn't support them
        clean_metadata = {k: v for k, v in entry.metadata.model_dump().items() if v is not None}
        
        self.collection.add(
            documents=[entry.content],
            metadatas=[clean_metadata],
            ids=[entry_id]
        )
        return entry_id

    def search_memories(self, query: str, n_results: int):
        results = self.collection.query(query_texts=[query], n_results=n_results)
        responses = []
        for i in range(len(results['ids'][0])):
            responses.append(MemoryResponse(
                id=results['ids'][0][i],
                content=results['documents'][0][i],
                metadata=results['metadatas'][0][i],
                distance=results['distances'][0][i]
            ))
        return responses

    def list_memories(self, limit: int = 10) -> List[MemoryResponse]:
        results = self.collection.get(limit=limit)
        responses = []
        for i in range(len(results['ids'])):
            responses.append(MemoryResponse(
                id=results['ids'][i],
                content=results['documents'][i],
                metadata=results['metadatas'][i]
            ))
        return responses

    def delete_memory(self, memory_id: str) -> bool:
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False

class OpenAIEngine(ILLMEngine):
    def __init__(self, api_key: str, base_url: str = None):
        # GitHub Models or Groq require a custom base_url
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1"
        ) if api_key else None

    def generate_response(self, query: str, context: list) -> str:
        context_str = "\n".join([f"- {doc}" for doc in context])
        
        if not self.client:
            return f"本地模式（未配置 API Key）: 我为您找到了以下相关记忆：\n{context_str}"
        
        prompt = f"基于以下记忆内容回答用户：\n{context_str}\n\n问题：{query}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI 接口调用失败: {str(e)}。检索到的背景：\n{context_str}"
