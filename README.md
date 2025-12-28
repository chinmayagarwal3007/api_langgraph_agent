# API Copilot Backend

Backend service for a conversational API testing and exploration assistant.

## Tech Stack
- FastAPI (async)
- LangGraph (workflow orchestration)
- Gemini 2.5 Flash (LLM)
- Postgres (Neon)
- FAISS (vector search)
- Redis (later)

## Run locally
```bash
uvicorn main:app --reload
