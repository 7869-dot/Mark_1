from pydantic import BaseModel

# ============================================================
# models.py — Data shapes for requests and responses
# ============================================================
# Pydantic automatically validates incoming data.
# If the frontend sends wrong/missing fields, FastAPI
# rejects it instantly with a clear error message.
# ============================================================

class ChatRequest(BaseModel):
    """
    Shape of data the FRONTEND must send to /api/chat
    
    Frontend connection:
        fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: "Hello",       ← required
                user_id: "user_123"     ← required (used later for memory)
            })
        })
    """
    message: str        # the user's chat message
    user_id: str        # unique ID per user (used later when you add memory)


class ChatResponse(BaseModel):
    """
    Shape of data the BACKEND sends back to the frontend.
    
    Frontend connection:
        const data = await res.json()
        console.log(data.reply)     ← the AI's response
        console.log(data.user_id)   ← echoed back for frontend state management
    """
    reply: str          # Gemini's response text
    user_id: str        # echoed back so frontend knows which user this belongs to