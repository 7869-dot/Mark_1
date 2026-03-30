from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class ChatRequest(BaseModel):
    """Shape of data the FRONTEND must send to /api/chat"""
    message: str
    user_id: str

class ChatResponse(BaseModel):
    """Shape of data the BACKEND sends back to the frontend."""
    reply: str
    user_id: str

class AgentRequest(BaseModel):
    user_id: str
    task_type: str
    message: str
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    reply: str
    data: Optional[Dict[str, Any]] = None

class PersonaSetupRequest(BaseModel):
    user_id: str
    job_context: str
    writing_samples: List[str]

class PersonaResponse(BaseModel):
    user_id: str
    has_persona: bool
    summary: str