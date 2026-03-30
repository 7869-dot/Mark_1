from schemas import AgentRequest, AgentResponse
from Capabilites.chat import handle_chat
from Capabilites.email import handle_email
from Capabilites.crm import handle_crm
from Capabilites.report_gen import handle_report

async def dispatch(request: AgentRequest) -> AgentResponse:
    task_type = request.task_type.lower()
    
    if task_type == "chat":
        return await handle_chat(request)
    elif task_type == "email" or task_type == "email_draft":
        return await handle_email(request)
    elif task_type == "crm" or task_type == "crm_update":
        return await handle_crm(request)
    elif task_type == "report" or task_type == "report_gen":
        return await handle_report(request)
    else:
        # Default behavior: chat
        return await handle_chat(request)
