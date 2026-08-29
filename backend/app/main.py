from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import ir, knowledge, chat, evaluation

app = FastAPI(
    title="Intelligent QA & Chatbot System API",
    description=(
        "Backend for Exercise 2: IR-based factoid QA, Knowledge-based QA, "
        "simple dialogue management, and evaluation."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local academic demo; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ir.router)
app.include_router(knowledge.router)
app.include_router(chat.router)
app.include_router(evaluation.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "qa-chatbot-backend"}
