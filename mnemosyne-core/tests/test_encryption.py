import pytest
from app.encryption import EncryptionManager
from app.services import ChromaStorage
from app.schemas import MemoryEntry, MemoryMetadata
import os
import shutil

def test_encryption_decryption():
    key = "secret_passphrase"
    manager = EncryptionManager(key)
    
    original_text = "This is a secret message."
    encrypted = manager.encrypt(original_text)
    assert encrypted != original_text
    
    decrypted = manager.decrypt(encrypted)
    assert decrypted == original_text

def test_wrong_key_fails():
    manager1 = EncryptionManager("key1")
    manager2 = EncryptionManager("key2")
    
    original_text = "Secret"
    encrypted = manager1.encrypt(original_text)
    
    decrypted = manager2.decrypt(encrypted)
    assert decrypted == "[DECRYPTION_FAILED]"

def test_storage_with_encryption():
    test_path = "./data/test_encrypted_storage"
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
    
    storage = ChromaStorage(path=test_path)
    encryptor = EncryptionManager("my_key")
    
    entry = MemoryEntry(content="Encrypted Secret", metadata=MemoryMetadata(category="top-secret"))
    storage.add_memory(entry, encryptor=encryptor)
    
    # 1. Search WITH encryptor
    results = storage.search_memories("Secret", n_results=1, encryptor=encryptor)
    assert results[0].content == "Encrypted Secret"
    
    # 2. Search WITHOUT encryptor (should see encrypted text)
    results_raw = storage.search_memories("Secret", n_results=1)
    assert results_raw[0].content != "Encrypted Secret"
    assert len(results_raw[0].content) > 20 # Fernet tokens are long
    
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
