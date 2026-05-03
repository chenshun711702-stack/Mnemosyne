# Task List: Project Mnemosyne

## 🟢 Completed
- [x] Initial design and business plan (`project_mnemosyne.md`).
- [x] SDD Folder structure and module initialization.
- [x] `schemas.py` - Pydantic model definitions.
- [x] `interfaces.py` - Abstract base classes for Storage and AI.
- [x] `services.py` - ChromaDB and OpenAI implementations.
- [x] `main.py` - FastAPI entry point with Dependency Injection.

## 🟡 In Progress
- [ ] Refining `demo.py` to match new SDD structure.
- [ ] Documenting API endpoints in Swagger/OpenAPI format.

## 🔴 Backlog (To Do)
- [ ] Task: Create `tests/test_storage.py` to verify vector persistence.
- [ ] Task: Add `.env.example` file for user configuration.
- [ ] Task: Initialize `frontend/` directory with a Vite+React setup.
- [ ] Task: Implement error handling for rate-limited AI calls.
