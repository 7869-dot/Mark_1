from schemas import AgentRequest, AgentResponse
from llm import generate_reply

async def handle_report(request: AgentRequest) -> AgentResponse:
    prompt = f"Generate a short report based on: {request.message}"
    reply = generate_reply(prompt)
    return AgentResponse(reply=reply, data={"report_status": "generated"})
