import pytest
from unittest.mock import MagicMock
from app.services import OpenAIEngine, ChromaStorage
from app.schemas import MemoryEntry
import os
import shutil

def test_sentiment_analysis_logic():
    # Mocking OpenAI client to avoid actual calls
    engine = OpenAIEngine(api_key="fake_key")
    engine.client = MagicMock()
    
    # Simulate GPT response for positive text
    engine.client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="Positive"))
    ]
    
    res = engine.analyze_sentiment("I love this project!")
    assert res == "Positive"

def test_sentiment_tagging_in_storage():
    test_path = "./data/test_sentiment_db"
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
    
    storage = ChromaStorage(path=test_path)
    # Since we use CLIP for embeddings now, we don't need to mock the embedding function
    # but we will manually set the sentiment as main.py would
    
    entry = MemoryEntry(
        content="Feeling great today!",
        metadata={"sentiment": "Positive"}
    )
    
    entry_id = storage.add_memory(entry)
    
    # Retrieve and verify
    results = storage.list_memories(limit=1)
    assert results[0].metadata["sentiment"] == "Positive"
    
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
