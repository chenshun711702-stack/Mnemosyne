# Task List: Project Mnemosyne

## 🟢 Completed
- [x] Initial design and business plan (`project_mnemosyne.md`).
- [x] SDD Folder structure and module initialization.
- [x] `schemas.py` - Pydantic model definitions.
- [x] `interfaces.py` - Abstract base classes for Storage and AI.
- [x] `services.py` - ChromaDB, OpenAI, and CLIP implementations.
- [x] `main.py` - FastAPI entry point with Multi-modal support.
- [x] `tests/test_storage.py` - Verified vector persistence.
- [x] `.env.example` - Added for user configuration.
- [x] `frontend/` - Artistic Bento-Box UI with Framer Motion.
- [x] Error handling for rate-limited AI calls (using `tenacity`).
- [x] Implement local-first data encryption (User-side key management).
- [x] Phase 3: Image-to-Vector support using local CLIP model.
- [x] Phase 3: Voice-to-Memory using **Local Whisper Model** (`small`).
- [x] Cognitive Review Loop for voice ingestion.
- [x] **Priority 2: Dockerization**: Created Dockerfiles and Compose setup for production deployment.

## 🟡 In Progress
- [ ] Optimizing Docker image sizes.
- [ ] Preparing Export/Import functionality.

## 🔴 Backlog (To Do)
- [ ] Task: Export/Import functionality for encrypted archives.
- [ ] Task: Sentiment trend analysis in Synthesis.
- [ ] Task: Edge-server auto-discovery.
