# Technical Specification: Project Mnemosyne

## 1. System Goals
To provide a high-fidelity, privacy-preserving digital cognitive archive using vector-based semantic retrieval and LLM synthesis.

## 2. Interface Definitions
### 2.1 Ingestion API
- **Endpoint**: `POST /ingest`
- **Input**: `MemoryEntry { content: string, metadata: object }`
- **Output**: `{ status: "success", id: string }`

### 2.3 Management API
- **Endpoint**: `GET /memories`
- **Output**: `List[MemoryResponse]`
- **Endpoint**: `DELETE /memories/{id}`
- **Output**: `{ status: "success" }`

## 3. Data Schema
- **Vector Space**: Cosine similarity on 384-dimensional embeddings (all-MiniLM-L6-v2).
- **Metadata Fields**: `timestamp` (ISO8601), `location` (String), `category` (Enum), `sentiment` (Float).

## 4. Constraint & Security
- **Data Locality**: Vectors stored in local persistent ChromaDB instances.
- **Privacy**: Zero-knowledge intent for future iterations.
