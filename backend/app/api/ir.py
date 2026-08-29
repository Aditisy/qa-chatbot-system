from fastapi import APIRouter, HTTPException

from ..models.schemas import IRQuestionRequest
from ..services.registry import ir_service

router = APIRouter(prefix="/api/ir", tags=["IR-Based QA"])


@router.post("/ask")
def ask(request: IRQuestionRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")
    result = ir_service.answer(question)
    return result


@router.get("/documents")
def list_documents():
    return {"documents": ir_service.list_documents()}
