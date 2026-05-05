import os
from typing import Optional
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
    entry_id = storage.add_memory(entry, encryptor=encryptor)
    return {"status": "success", "id": entry_id}

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

@app.post("/ingest/voice")
async def ingest_voice(
    file: UploadFile = File(...),
    encryptor: Optional[EncryptionManager] = Depends(get_encryptor)
):
    audio_bytes = await file.read()
    
    # 1. Transcribe via Whisper
    transcript = llm.transcribe_audio(audio_bytes)
    
    if transcript.startswith("[Error:"):
        return {"status": "error", "message": transcript}

    # 2. Store as text memory
    entry = MemoryEntry(
        content=transcript,
        metadata={"source": "voice", "filename": file.filename}
    )
    entry_id = storage.add_memory(entry, encryptor=encryptor)
    
    return {"status": "success", "id": entry_id, "transcript": transcript}

@app.post("/query")
async def query(request: QueryRequest, encryptor: Optional[EncryptionManager] = Depends(get_encryptor)):
    return storage.search_memories(request.query, request.n_results, encryptor=encryptor)

@app.get("/memories")
async def list_mems(limit: int = 20, encryptor: Optional[EncryptionManager] = Depends(get_encryptor)):
    return storage.list_memories(limit, encryptor=encryptor)

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
