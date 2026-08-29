from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class IRQuestionRequest(BaseModel):
    question: str


class KBQuestionRequest(BaseModel):
    question: str


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ResetRequest(BaseModel):
    session_id: str = "default"
