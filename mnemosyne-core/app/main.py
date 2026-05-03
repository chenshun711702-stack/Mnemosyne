import os
from fastapi import FastAPI, Depends
from app.schemas import MemoryEntry, QueryRequest, ChatRequest, ChatResponse
from app.services import ChromaStorage, OpenAIEngine
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Project Mnemosyne (SDD Architecture)")

# Dependency Injection Setup
storage = ChromaStorage(path="./data/chroma")
llm = OpenAIEngine(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

@app.post("/ingest")
async def ingest(entry: MemoryEntry):
    entry_id = storage.add_memory(entry)
    return {"status": "success", "id": entry_id}

@app.post("/query")
async def query(request: QueryRequest):
    return storage.search_memories(request.query, request.n_results)

@app.get("/memories")
async def list_mems(limit: int = 20):
    return storage.list_memories(limit)

@app.delete("/memories/{memory_id}")
async def delete_mem(memory_id: str):
    success = storage.delete_memory(memory_id)
    return {"status": "success" if success else "failed"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Spec-defined workflow: Search -> Generate
    memories = storage.search_memories(request.message, n_results=5)
    context = [m.content for m in memories]
    
    answer = llm.generate_response(request.message, context)
    
    return ChatResponse(
        answer=answer,
        sources=context
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
