from abc import ABC, abstractmethod
from typing import List
from .schemas import MemoryEntry, MemoryResponse

class IMemoryStorage(ABC):
    @abstractmethod
    def add_memory(self, entry: MemoryEntry, encryptor=None) -> str:
        pass

    @abstractmethod
    def add_image_memory(self, image_bytes: bytes, metadata: dict, encryptor=None) -> str:
        pass

    @abstractmethod
    def search_memories(self, query: str, n_results: int, encryptor=None) -> List[MemoryResponse]:
        pass

    @abstractmethod
    def list_memories(self, limit: int, encryptor=None) -> List[MemoryResponse]:
        pass

    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        pass

class ILLMEngine(ABC):
    @abstractmethod
    def generate_response(self, query: str, context: List[str]) -> str:
        pass
