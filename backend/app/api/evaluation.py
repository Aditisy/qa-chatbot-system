from fastapi import APIRouter

from ..services.registry import evaluator

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation"])


@router.get("")
def get_evaluation():
    return evaluator.full_report()
