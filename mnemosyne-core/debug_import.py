import json
from app.schemas import MemoryEntry, MemoryMetadata

# Sample from export
export_data = {
    "id": "mem_123",
    "content": "Test content",
    "metadata": {
        "timestamp": "2026-05-05T12:45:56.898921",
        "location": "Local Browser",
        "is_image": True # This key exists in export but let's see if MemoryEntry likes it
    }
}

try:
    # Try to initialize MemoryEntry with the dict
    entry = MemoryEntry(
        content=export_data["content"],
        metadata=export_data["metadata"]
    )
    print("Successfully initialized MemoryEntry")
    print(entry.model_dump())
except Exception as e:
    print(f"Failed to initialize MemoryEntry: {e}")
