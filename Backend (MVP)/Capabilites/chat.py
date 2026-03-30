from schemas import AgentRequest, AgentResponse
from llm import generate_reply

async def handle_chat(request: AgentRequest) -> AgentResponse:
    reply = generate_reply(request.message)
    return AgentResponse(reply=reply)
