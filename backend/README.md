# Backend — Intelligent QA & Chatbot System

FastAPI backend implementing IR-based QA, Knowledge-based QA, a rule-based dialogue manager, and an evaluation module.

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

The API is now live at `http://localhost:8000`. Interactive docs (Swagger UI) at `http://localhost:8000/docs`.

## Endpoints

| Method | Path                  | Purpose                                   |
|--------|-----------------------|--------------------------------------------|
| GET    | `/api/health`         | Health check                               |
| POST   | `/api/ir/ask`         | IR-based factoid QA                        |
| GET    | `/api/ir/documents`   | List the IR corpus                         |
| POST   | `/api/knowledge/ask`  | Knowledge-based QA                         |
| GET    | `/api/knowledge/entities` | List KB entities                       |
| POST   | `/api/chat`           | Dialogue turn (`message`, `session_id`)    |
| POST   | `/api/chat/reset`     | Reset a dialogue session                   |
| GET    | `/api/evaluation`     | Full EM/F1/Accuracy report                 |

## Quick test

```bash
curl -X POST http://localhost:8000/api/ir/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Who developed the theory of relativity?"}'

curl -X POST http://localhost:8000/api/knowledge/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the symptoms of Diabetes?"}'
```

## Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app + router registration
│   ├── api/                     # Route handlers (thin controllers)
│   │   ├── ir.py
│   │   ├── knowledge.py
│   │   ├── chat.py
│   │   └── evaluation.py
│   ├── models/schemas.py        # Pydantic request models
│   └── services/                # Actual NLP/QA logic
│       ├── retrieval.py         # TF-IDF indexing + cosine similarity retrieval
│       ├── qa_service.py        # Rule-based extractive answer-span extraction
│       ├── ir_service.py        # Orchestrates the IR pipeline
│       ├── knowledge_service.py # Entity/relation detection + KB query
│       ├── dialogue_manager.py  # Intent detection, context, coreference
│       ├── evaluation.py        # EM / F1 / Accuracy computation
│       └── registry.py          # Shared service singletons
├── data/
│   ├── ir_documents/            # 8 sample .txt documents (science, history, geography, tech, education)
│   ├── healthcare_knowledge_base.csv # 15 diseases, six relations
│   └── evaluation_dataset.json  # 17 IR Qs, 15 KB Qs, 7 dialogue turns
└── requirements.txt
```
