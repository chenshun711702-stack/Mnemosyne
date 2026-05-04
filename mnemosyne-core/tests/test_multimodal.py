import pytest
import os
import shutil
from app.services import ChromaStorage
from app.schemas import MemoryEntry
from PIL import Image
import io

def test_multimodal_combined():
    test_path = "./data/test_multimodal_combined"
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
    
    storage = ChromaStorage(path=test_path)
    
    # 1. Test Image Ingestion
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    entry_id = storage.add_image_memory(img_bytes, metadata={"type": "test_image"})
    assert entry_id.startswith("img_")
    
    # 2. Test Cross-modal Search (Text find Image)
    results = storage.search_memories("a red square", n_results=1)
    assert len(results) == 1
    assert results[0].metadata["is_image"] == True

    # 3. Test Text Ingestion
    storage.add_memory(MemoryEntry(content="The capital of France is Paris."))
    
    # 4. Test Cross-modal Search (Text find Text)
    res_text = storage.search_memories("Paris", n_results=1)
    assert "Paris" in res_text[0].content
    
    # Clean up
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
