from fastapi import APIRouter, HTTPException

from ..models.schemas import KBQuestionRequest
from ..services.registry import knowledge_service

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge-Based QA"])


@router.post("/ask")
def ask(request: KBQuestionRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")
    result = knowledge_service.query(question)
    return result


@router.get("/entities")
def list_entities():
    return {"entities": knowledge_service.list_entities()}
