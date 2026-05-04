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
- [x] Documented lessons learned for PostCSS/Tailwind configuration.

## 🟡 In Progress
- [ ] Stabilizing CLIP performance on various image types.
- [ ] Designing the Voice-to-Memory (Whisper) integration.

## 🔴 Backlog (To Do)
- [ ] Task: Integrate Whisper for voice-to-memory ingestion.
- [ ] Task: Dockerization for edge-server deployment.
- [ ] Task: Export/Import functionality for encrypted archives.
