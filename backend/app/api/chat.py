from fastapi import APIRouter, HTTPException

from ..models.schemas import ChatRequest, ResetRequest
from ..services.registry import dialogue_manager

router = APIRouter(prefix="/api/chat", tags=["Chat / Dialogue"])


@router.post("")
def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message must not be empty.")
    result = dialogue_manager.handle_message(request.session_id, message)
    return result


@router.post("/reset")
def reset(request: ResetRequest):
    state = dialogue_manager.reset_session(request.session_id)
    return {"status": "reset", "session_state": state}
