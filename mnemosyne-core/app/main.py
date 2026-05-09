import os
import json
import base64
from typing import Optional, Any
from datetime import datetime
from fastapi import FastAPI, Depends, Header, UploadFile, File
from app.schemas import MemoryEntry, MemoryMetadata, QueryRequest, ChatRequest, ChatResponse
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

def flatten_json(data: Any, prefix: str = "") -> list:
    """Recursively flattens JSON into a list of descriptive strings."""
    items = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix} {key}" if prefix else key
            items.extend(flatten_json(value, new_prefix))
    elif isinstance(data, list):
        for i, value in enumerate(data):
            items.extend(flatten_json(value, f"{prefix} item {i+1}"))
    else:
        items.append(f"{prefix}: {data}")
    return items

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
        "version": "0.6.0",
        "exported_at": datetime.now().isoformat(),
        "memories": [m.model_dump() for m in memories]
    }

@app.post("/import")
async def import_archive(
    file: UploadFile = File(...),
    encryptor: Optional[EncryptionManager] = Depends(get_encryptor)
):
    content = await file.read()
    try:
        data = json.loads(content)
    except Exception as e:
        return {"status": "error", "message": f"Invalid JSON format: {str(e)}"}

    memories_to_import = []
    
    # Check if it's a standard Mnemosyne Export
    if isinstance(data, dict) and "memories" in data:
        for m in data["memories"]:
            metadata_dict = m.get("metadata", {})
            if metadata_dict.get("is_image"):
                img_data = base64.b64decode(m["content"])
                storage.add_image_memory(img_data, metadata=metadata_dict, encryptor=encryptor)
            else:
                entry = MemoryEntry(content=m["content"], metadata=MemoryMetadata(**metadata_dict))
                if not entry.metadata.sentiment:
                    entry.metadata.sentiment = llm.analyze_sentiment(entry.content)
                storage.add_memory(entry, encryptor=encryptor)
        return {"status": "success", "imported_count": len(data["memories"])}

    # If it's a generic JSON (like the family archive), flatten it
    print(f"[{datetime.now()}] Detected non-standard JSON. Invoking Cognitive Parser...")
    flat_items = flatten_json(data)
    for item in flat_items:
        # Optimized: Skip GPT sentiment analysis for data fragments to prevent timeouts
        entry = MemoryEntry(
            content=item,
            metadata=MemoryMetadata(category="Imported Profile", source="json_import", sentiment="Neutral")
        )
        storage.add_memory(entry, encryptor=encryptor)
        
    return {"status": "success", "imported_count": len(flat_items)}

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

@app.get("/stats/vibe")
async def vibe_stats():
    # Retrieve recent memories (limit to 100 for stats)
    memories = storage.list_memories(limit=100)
    
    stats = {}
    for m in memories:
        # Extract date YYYY-MM-DD
        ts = m.metadata.get("timestamp")
        if not ts: continue
        
        day = ts.split("T")[0]
        sentiment = m.metadata.get("sentiment", "Neutral")
        
        if day not in stats:
            stats[day] = {"Positive": 0, "Negative": 0, "Neutral": 0}
        
        stats[day][sentiment] += 1
    
    # Sort by date
    sorted_stats = dict(sorted(stats.items()))
    return sorted_stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
