# persona-ai

Production-oriented **Personal AI Persona** API: FastAPI + **PostgreSQL** + **pgvector**, JWT auth, long-term memory ingestion (chunk → embed → store), and vector retrieval for agent-style behavior. Built for the first ~100 users with a clear path to scale.

## Stack

- Python **3.12+**, **FastAPI**, **Pydantic v2**, **SQLAlchemy 2.0** (async), **Alembic**
- **asyncpg**, **pgvector** (HNSW index on embeddings)
- **bcrypt** passwords, **python-jose** JWT
- **slowapi** rate limits, **httpx** for OpenAI-compatible embeddings

## Quick start (Docker)

From `persona-ai/`:

1. Copy environment template and set a strong `SECRET_KEY` (32+ characters):

   ```bash
   cp .env.example .env
   ```

2. Start Postgres (pgvector) and API:

   ```bash
   docker compose up --build
   ```

   - API: http://127.0.0.1:8000  
   - OpenAPI: http://127.0.0.1:8000/api/v1/docs  
   - Health: http://127.0.0.1:8000/health  

Compose sets `EMBEDDING_FAKE=true` by default so embeddings work **without** an API key (deterministic vectors — good for local demos, not for semantic quality).

## Local development (without rebuilding the API container)

1. Start only the database:

   ```bash
   docker compose up -d db
   ```

2. Create venv, install app + dev deps:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. Configure `.env` (match compose credentials if using the bundled Postgres):

   ```env
   DATABASE_URL=postgresql+asyncpg://persona:persona@localhost:5432/persona
   SECRET_KEY=your-32-plus-character-secret-key-here
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   EMBEDDING_FAKE=true
   ```

4. Run migrations:

   ```bash
   alembic upgrade head
   ```

5. Run API:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## First user, persona, memory, retrieval

1. **Register** (JSON):

   ```bash
   curl -s -X POST http://127.0.0.1:8000/api/v1/users/register ^
     -H "Content-Type: application/json" ^
     -d "{\"email\":\"you@example.com\",\"password\":\"yourpassword\"}"
   ```

2. **Login** (JSON) and save token:

   ```bash
   curl -s -X POST http://127.0.0.1:8000/api/v1/users/login ^
     -H "Content-Type: application/json" ^
     -d "{\"email\":\"you@example.com\",\"password\":\"yourpassword\"}"
   ```

3. **Create persona** (note trailing slash on collection):

   ```bash
   curl -s -X POST http://127.0.0.1:8000/api/v1/personas/ ^
     -H "Authorization: Bearer YOUR_TOKEN" ^
     -H "Content-Type: application/json" ^
     -d "{\"name\":\"My twin\",\"description\":\"Mirrors my style\",\"system_prompt\":\"Be concise.\"}"
   ```

4. **Ingest memory** (replace `PERSONA_ID`):

   ```bash
   curl -s -X POST http://127.0.0.1:8000/api/v1/personas/PERSONA_ID/memories/ingest ^
     -H "Authorization: Bearer YOUR_TOKEN" ^
     -H "Content-Type: application/json" ^
     -d "{\"source_type\":\"profile\",\"content\":\"I prefer direct feedback and morning runs.\"}"
   ```

5. **Retrieve** (vector search):

   ```bash
   curl -s -X POST http://127.0.0.1:8000/api/v1/personas/PERSONA_ID/memories/retrieve ^
     -H "Authorization: Bearer YOUR_TOKEN" ^
     -H "Content-Type: application/json" ^
     -d "{\"query\":\"What are my exercise habits?\",\"limit\":5}"
   ```

Use **Swagger** at `/api/v1/docs` for OAuth2 password flow (`POST /api/v1/users/token`) and Bearer auth.

## Seed script

With DB up and migrations applied:

```bash
python scripts/seed_data.py
```

Creates `seed@persona-ai.local` / `seedpassword123`, a persona, and sample memories (uses your configured embedding mode).

## Real embeddings (OpenAI-compatible)

In `.env`:

```env
EMBEDDING_FAKE=false
EMBEDDING_API_KEY=sk-...
EMBEDDING_API_BASE=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
```

The initial Alembic migration creates a **1536-dimensional** `vector` column. If you change dimensions, add a new migration.

## Tests

```bash
pytest
```

## Project layout

See repository tree: `app/` (API, services, models), `alembic/` (migrations), `tests/`, `scripts/`.

## Notes

- `alembic.ini` lives at the project root (required for `alembic upgrade head` alongside `alembic/env.py`).
- Rate limits default to `RATE_LIMIT_DEFAULT` / `RATE_LIMIT_AUTH` (see `.env.example`).
- `GET /api/v1/ready` checks database connectivity; `GET /health` is a simple liveness probe.
