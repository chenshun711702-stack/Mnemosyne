# Mnemosyne Docker Deployment Guide

This guide explains how to deploy the entire Project Mnemosyne stack using Docker.

## 🚀 Quick Start

1.  Ensure you have **Docker** and **Docker Compose** installed.
2.  From the project root, run:
    ```bash
    docker-compose up --build
    ```
3.  Access the UI: **[http://localhost:3000](http://localhost:3000)**
4.  Access the API (Swagger): **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 🏗 Architecture

The `docker-compose.yml` file orchestrates two main services:

### 1. Backend (`mnemosyne-backend`)
- **Base**: Python 3.9-slim.
- **Tools**: Includes `ffmpeg` for local voice transcription.
- **API**: FastAPI running on port 8000.

### 2. Frontend (`mnemosyne-frontend`)
- **Base**: Nginx (serving a React/Vite production build).
- **Port**: Exposed on port 3000.
- **Proxy**: Automatically forwards `/api/*` requests to the backend container.

---

## 💾 Data & Model Persistence

Mnemosyne uses Docker **Volumes** to ensure your data is never lost when a container stops.

-   **`whisper_cache`**: Stores the downloaded Whisper models (e.g., `small.pt`).
-   **`clip_cache`**: Stores the CLIP visual embedding models.
-   **`./mnemosyne-core/data`**: A bind-mount that stores your local `chroma.sqlite3` vector database.

---

## ⚙️ Configuration

The system automatically reads your environment variables from **`mnemosyne-core/.env`**. 

**Required Keys:**
- `OPENAI_API_KEY`: Required for the Synthesis (AI Chat) feature.
- `OPENAI_BASE_URL`: Optional (for Azure/GitHub models).

---

## 🛠 Useful Commands

-   **Stop the system**: `docker-compose down`
-   **View logs**: `docker-compose logs -f`
-   **Full Reset (Clears models)**: `docker-compose down -v`
-   **Update code and rebuild**: `docker-compose up --build -d`

---
*Karpathy Mode: Minimalist, Isolated, Reproducible.*
