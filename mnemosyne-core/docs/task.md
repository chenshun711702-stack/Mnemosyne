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
- [x] **Cognitive Review Loop**: Added a two-step "Transcribe then Review" flow for voice ingestion.
- [x] Upgraded Whisper model to `small` for improved recognition accuracy.
- [x] Multi-language support (EN/ZH) for voice recognition.

## 🟡 In Progress
- [ ] Optimization of local model loading times.
- [ ] Preparation for Priority 2: Dockerization.

## 🔴 Backlog (To Do)
- [ ] Task: Dockerization for edge-server deployment.
- [ ] Task: Export/Import functionality for encrypted archives.
- [ ] Task: Sentiment trend analysis in Synthesis.
