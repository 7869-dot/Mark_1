from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import ChatRequest, ChatResponse
from llm import generate_reply

app = FastAPI(title="Mark_1 Backend MVP")

# Allow all origins for the MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Endpoint that receives user chat message and returns the LLM reply.
    """
    # Get reply from LLM using the provided user message
    reply_text = generate_reply(request.message)
    
    # Return matched response format
    return ChatResponse(
        reply=reply_text,
        user_id=request.user_id
    )

@app.get("/")
def root():
    return {"message": "Backend is running!"}

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is perfectly healthy!"}

@app.get("/api/health")
def api_health_check():
    return {"status": "ok", "message": "API is perfectly healthy!"}
