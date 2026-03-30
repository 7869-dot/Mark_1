from schemas import AgentRequest, AgentResponse
from Persona.store import load_persona
from llm import generate_reply

async def handle_email(request: AgentRequest) -> AgentResponse:
    persona = load_persona(request.user_id)
    style_context = ""
    if persona:
        style_context = f"Use this writing style: {persona['style_summary']}\n"
    
    prompt = f"{style_context}Draft an email for the following request: {request.message}"
    reply = generate_reply(prompt)
    
    return AgentResponse(reply=reply, data={"email_status": "drafted"})
