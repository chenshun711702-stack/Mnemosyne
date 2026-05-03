import pytest
import os
import shutil
from app.services import ChromaStorage
from app.schemas import MemoryEntry, MemoryMetadata

@pytest.fixture
def temp_storage():
    # Setup: Create a temporary test database
    test_path = "./data/test_chroma"
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
    
    storage = ChromaStorage(path=test_path)
    yield storage
    
    # Teardown: Clean up
    if os.path.exists(test_path):
        shutil.rmtree(test_path)

def test_add_and_search_memory(temp_storage):
    # 1. Prepare data
    entry = MemoryEntry(
        content="Test memory about artificial intelligence.",
        metadata=MemoryMetadata(category="tech")
    )
    
    # 2. Add to storage
    entry_id = temp_storage.add_memory(entry)
    assert entry_id.startswith("mem_")
    
    # 3. Search and verify
    results = temp_storage.search_memories("What is this about AI?", n_results=1)
    assert len(results) == 1
    assert "artificial intelligence" in results[0].content
    assert results[0].metadata["category"] == "tech"
