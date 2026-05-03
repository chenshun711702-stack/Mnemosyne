# SAD: Project Mnemosyne System Architecture Design

## 1. Architecture Overview
Mnemosyne follows a layered architecture to decouple data ingestion from AI-driven synthesis.

### 1.1 Ingestion Layer (The Senses)
Responsible for receiving raw data from mobile apps, wearables, or web extensions. Normalizes data into a standard JSON format before passing to the backend.

### 1.2 Core Service Layer (The Nervous System)
A FastAPI-based RESTful service that manages data flow, performs validation, and orchestrates calls to the Vector DB and LLM providers.

### 1.3 Knowledge Storage Layer (The Memory)
*   **Vector Database**: ChromaDB (Local) or Pinecone (Cloud) for storing embeddings.
*   **Object Storage**: AWS S3/Arweave for raw files (images, audio).

### 1.4 Intelligence Layer (The Brain)
*   **Embedding Engine**: Converts text/images into vectors.
*   **LLM Engine**: Generates responses using RAG.

## 2. Data Flow
1.  **Input**: User records a thought.
2.  **Processing**: Service calls Embedding Engine to vectorize the text.
3.  **Storage**: Vector + Metadata saved in Vector DB.
4.  **Retrieval**: On query, system finds top-K similar vectors.
5.  **Synthesis**: LLM uses these vectors as context to generate an answer.

## 3. Technology Stack
*   **Language**: Python 3.10+
*   **Framework**: FastAPI
*   **Database**: ChromaDB
*   **AI**: OpenAI API / local Transformers
