# API & Data Schema Design

## 1. Data Models (Pydantic)

### 1.1 MemoryEntry
The primary unit of data storage.
```python
{
    "content": str,        # The raw text of the memory
    "metadata": {          # Flexible key-value store
        "location": str,   # Optional: GPS or city name
        "category": str,   # Optional: travel, work, etc.
        "sentiment": float # Optional: -1.0 to 1.0
        "timestamp": str   # ISO format
    }
}
```

### 1.2 ChatRequest
Input for the RAG conversation.
```python
{
    "message": str,      # User question
    "user_id": str       # For future multi-user support
}
```

## 2. API Endpoints

### POST `/ingest`
Adds a new memory fragment.
*   **Response**: `200 OK` with `id` and `timestamp`.

### POST `/query`
Performs raw vector search.
*   **Request**: `{"query": str, "n_results": int}`
*   **Response**: List of closest matches with distances.

### POST `/chat`
Generates a response using RAG.
*   **Request**: `ChatRequest`
*   **Response**: `{"answer": str, "sources": list}`

### GET `/memories`
Lists all memories (with pagination).
*   **Parameters**: `limit` (int, optional)
*   **Response**: List of `MemoryResponse` objects.

### DELETE `/memories/{memory_id}`
Deletes a specific memory.
*   **Parameters**: `memory_id` (str, path)
*   **Response**: `{"status": "success" | "failed"}`

## 3. Vector Database Schema
*   **Collection Name**: `memories`
*   **Distance Metric**: Cosine Similarity
*   **Embedding Model**: `all-MiniLM-L6-v2` (via ChromaDB default)
