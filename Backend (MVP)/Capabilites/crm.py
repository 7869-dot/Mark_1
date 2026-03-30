from schemas import AgentRequest, AgentResponse
from llm import generate_reply

async def handle_crm(request: AgentRequest) -> AgentResponse:
    prompt = f"Extract CRM update details from this instruction: {request.message}"
    reply = generate_reply(prompt)
    return AgentResponse(reply=reply, data={"crm_status": "updated"})
