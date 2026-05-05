import os
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, Depends, Header, UploadFile, File
from app.schemas import MemoryEntry, QueryRequest, ChatRequest, ChatResponse
from app.services import ChromaStorage, OpenAIEngine
from app.encryption import EncryptionManager
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Project Mnemosyne (SDD Architecture)")

# Dependency Injection Setup
storage = ChromaStorage(path="./data/chroma")
llm = OpenAIEngine(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

def get_encryptor(x_encryption_key: Optional[str] = Header(None)):
    if x_encryption_key:
        return EncryptionManager(x_encryption_key)
    return None

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...)
):
    audio_bytes = await file.read()
    transcript = llm.transcribe_audio(audio_bytes)
    
    if transcript.startswith("[Error:"):
        return {"status": "error", "message": transcript}
    
    return {"status": "success", "transcript": transcript}

@app.post("/ingest")
async def ingest(entry: MemoryEntry, encryptor: Optional[EncryptionManager] = Depends(get_encryptor)):
    # Priority 5: Automatic Sentiment Analysis
    if not entry.metadata.sentiment:
        entry.metadata.sentiment = llm.analyze_sentiment(entry.content)
    
    entry_id = storage.add_memory(entry, encryptor=encryptor)
    return {"status": "success", "id": entry_id, "sentiment": entry.metadata.sentiment}

@app.post("/ingest/image")
async def ingest_image(
    file: UploadFile = File(...),
    encryptor: Optional[EncryptionManager] = Depends(get_encryptor)
):
    image_bytes = await file.read()
    entry_id = storage.add_image_memory(
        image_bytes=image_bytes, 
        metadata={"filename": file.filename},
        encryptor=encryptor
    )
    return {"status": "success", "id": entry_id}

@app.post("/query")
async def query(request: QueryRequest, encryptor: Optional[EncryptionManager] = Depends(get_encryptor)):
    return storage.search_memories(request.query, request.n_results, encryptor=encryptor)

@app.get("/memories")
async def list_mems(limit: int = 20, encryptor: Optional[EncryptionManager] = Depends(get_encryptor)):
    return storage.list_memories(limit, encryptor=encryptor)

@app.get("/export")
async def export_archive(encryptor: Optional[EncryptionManager] = Depends(get_encryptor)):
    memories = storage.list_memories(limit=10000, encryptor=None)
    return {
        "project": "Mnemosyne",
        "version": "0.5.0",
        "exported_at": datetime.now().isoformat(),
        "memories": [m.model_dump() for m in memories]
    }

@app.post("/import")
async def import_archive(
    file: UploadFile = File(...),
    encryptor: Optional[EncryptionManager] = Depends(get_encryptor)
):
    import json
    content = await file.read()
    data = json.loads(content)
    
    memories = data.get("memories", [])
    count = 0
    for m in memories:
        entry = MemoryEntry(
            content=m["content"],
            metadata=m["metadata"]
        )
        # Re-analyze sentiment if missing in old archive
        if not entry.metadata.sentiment:
            entry.metadata.sentiment = llm.analyze_sentiment(entry.content)
            
        storage.add_memory(entry, encryptor=encryptor)
        count += 1
        
    return {"status": "success", "imported_count": count}

@app.delete("/memories/{memory_id}")
async def delete_mem(memory_id: str):
    success = storage.delete_memory(memory_id)
    return {"status": "success" if success else "failed"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, encryptor: Optional[EncryptionManager] = Depends(get_encryptor)):
    memories = storage.search_memories(request.message, n_results=5, encryptor=encryptor)
    context = [m.content for m in memories]
    
    answer = llm.generate_response(request.message, context)
    
    return ChatResponse(
        answer=answer,
        sources=context
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
