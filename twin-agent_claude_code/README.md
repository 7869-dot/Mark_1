# Twin Agent

Autonomous AI agent core — the backend of the digital twin system.

The agent reads email, posts to Slack and Twitter, browses the web,
and remembers context across sessions. Built to be extended.

---

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/yourname/twin-agent
cd twin-agent

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
playwright install chromium        # For browser tools
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env — add your OpenAI or Anthropic API key at minimum
```

### 3. Seed memory and set up persona

```bash
python scripts/seed_memory.py
# Edit data/persona.json to customize the agent's identity
```

### 4. Run your first task

```bash
# Single task
python scripts/run_agent.py "Search the web for the latest news on AI agents"

# Interactive mode
python scripts/run_agent.py --interactive

# With full event log
python scripts/run_agent.py --verbose "Browse to example.com and summarize it"
```

### 5. Start the API server

```bash
uvicorn api.main:app --reload
```

API docs available at `http://localhost:8000/docs`

---

## Project structure

```
twin-agent/
├── agent/
│   ├── core.py          # ReAct loop — the agent brain
│   ├── executor.py      # Wires tools + memory into one agent instance
│   └── persona.py       # Identity layer
├── memory/
│   ├── short_term.py    # In-context sliding window
│   ├── episodic.py      # SQLite audit log of all actions
│   ├── semantic.py      # ChromaDB vector store
│   └── retriever.py     # Unified memory interface
├── integrations/
│   ├── base.py          # BaseTool + ToolRegistry
│   ├── gmail.py         # Read, send, search email
│   ├── slack.py         # Send, read, list channels
│   ├── twitter.py       # Post, read timeline, search
│   └── browser.py       # Fetch pages, search web
├── llm/
│   ├── client.py        # litellm wrapper (swap models via .env)
│   └── prompts.py       # All system prompts
├── config/
│   ├── settings.py      # Pydantic settings (loaded from .env)
│   └── logging.py       # Structured logging
├── api/
│   ├── main.py          # FastAPI app
│   └── routes/
│       ├── agent.py     # POST /agent/run, GET /agent/session/{id}
│       └── memory.py    # POST /memory/search, POST /memory/store
└── scripts/
    ├── run_agent.py     # CLI entrypoint
    └── seed_memory.py   # Load initial persona context
```

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/agent/run` | Run a task |
| `GET` | `/agent/sessions` | List recent session IDs |
| `GET` | `/agent/session/{id}` | Full event log for a session |
| `POST` | `/memory/search` | Semantic search over memory |
| `POST` | `/memory/store` | Store a fact manually |
| `DELETE` | `/memory/{id}` | Delete a memory entry |
| `GET` | `/health` | Server health and stats |

### Example: run a task

```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "Read my last 3 emails and summarize them"}'
```

---

## Switching models

Change `LLM_MODEL` in `.env` — no code changes needed:

```bash
LLM_MODEL=gpt-4o                          # OpenAI (default)
LLM_MODEL=claude-3-5-sonnet-20241022      # Anthropic
LLM_MODEL=groq/llama-3.1-70b-versatile   # Groq (fast + cheap)
```

## Adding a new integration

1. Create `integrations/mytool.py` extending `BaseTool`
2. Implement `name`, `description`, `parameters`, and `run()`
3. Register it in `agent/executor.py`:

```python
from integrations.mytool import MyTool
registry.register(MyTool())
```

That's it. The agent will automatically discover and use it.

---

## Running tests

```bash
pytest tests/ -v
pytest tests/test_memory.py -v        # Memory only (no API keys needed)
pytest tests/test_agent_loop.py -v    # Agent loop with mocked LLM
```

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | One of these | LLM provider |
| `ANTHROPIC_API_KEY` | One of these | LLM provider |
| `LLM_MODEL` | No | Model to use (default: `gpt-4o`) |
| `GMAIL_CLIENT_ID` | No | Enables Gmail tools |
| `GMAIL_CLIENT_SECRET` | No | Enables Gmail tools |
| `SLACK_BOT_TOKEN` | No | Enables Slack tools |
| `TWITTER_API_KEY` | No | Enables Twitter tools |
| `TWITTER_BEARER_TOKEN` | No | Enables Twitter search |

Tools without credentials are silently skipped — the agent runs with whatever is configured.
