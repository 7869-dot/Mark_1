from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import ChatRequest, ChatResponse, AgentRequest, AgentResponse, PersonaSetupRequest, PersonaResponse
from llm import generate_reply
from Agents.router import dispatch
from Persona.store import save_persona, load_persona

app = FastAPI(title="Mark_1 Backend MVP")

# ── CORS ──────────────────────────────────────────────────────────────────────
# Fixed: CORSMiddleware takes no keyword args on the class itself.
# allow_origins controls which frontends can call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Legacy chat endpoint (keep working, don't break frontend) ─────────────────
@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """Original endpoint — untouched so your frontend keeps working."""
    reply_text = generate_reply(request.message)
    return ChatResponse(reply=reply_text, user_id=request.user_id)


# ── Agent endpoint (new) ──────────────────────────────────────────────────────
@app.post("/api/agent/run", response_model=AgentResponse)
async def agent_run(request: AgentRequest):
    """
    New main endpoint. Routes to the right capability based on task_type.

    Frontend sends:
        {
            "user_id": "user_123",
            "task_type": "email_draft",   <- or crm_update / report_gen / chat
            "message": "Draft a follow-up to Sarah about the proposal",
            "context": {}                 <- optional extra data
        }
    """
    return await dispatch(request)


# ── Persona endpoints (new) ───────────────────────────────────────────────────
@app.post("/api/persona/setup", response_model=PersonaResponse)
async def persona_setup(request: PersonaSetupRequest):
    """
    Call once during onboarding. Feed it the user's writing samples
    and job context — it builds their style profile.
    """
    from llm import generate_style_summary
    style_summary = await generate_style_summary(request.writing_samples)
    save_persona(
        user_id=request.user_id,
        job_context=request.job_context,
        writing_samples=request.writing_samples,
        style_summary=style_summary,
    )
    return PersonaResponse(user_id=request.user_id, has_persona=True, summary=style_summary)


@app.get("/api/persona/{user_id}", response_model=PersonaResponse)
def persona_get(user_id: str):
    """Check what the agent knows about a user."""
    persona = load_persona(user_id)
    if not persona:
        return PersonaResponse(user_id=user_id, has_persona=False, summary="No persona yet.")
    return PersonaResponse(user_id=user_id, has_persona=True, summary=persona["style_summary"])


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Mark_1 backend is running"}

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is perfectly healthy!"}

@app.get("/api/health")
def api_health_check():
    return {"status": "ok", "message": "API is perfectly healthy!"}