# Intelligent QA & Chatbot System
### Exercise 2 — AML23702 Advanced Natural Language Processing

A two-mode Question Answering and Chatbot system: **IR-based factoid QA** over an unstructured document corpus, and **Knowledge-based QA** over a structured knowledge base, tied together by a **simple frame-based dialogue manager** and a real, computed **evaluation** module.

Stack: **FastAPI (Python)** backend + **React / Vite / Tailwind CSS** frontend. No Streamlit. No external paid API required — everything runs locally.

---

## 1. Quick Start

**Terminal 1 — backend**
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend**
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend proxies `/api/*` calls to the backend on port 8000.

**Run the evaluation from the command line instead of the UI:**
```bash
cd backend
python3 -c "from app.services.registry import evaluator; import json; print(json.dumps(evaluator.full_report(), indent=2))"
```

---

## 2. Architecture

```
                    ┌──────────────────────┐
                    │      HOME PAGE       │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                ↓                             ↓
       ┌─────────────────┐          ┌──────────────────┐
       │   IR-BASED QA    │          │ KNOWLEDGE-BASED  │
       │                  │          │       QA         │
       │ TF-IDF retrieval │          │ Entity detection │
       │ ↓ Passage rank   │          │ ↓ Relation detect│
       │ ↓ Extractive QA  │          │ ↓ KB query        │
       │ Answer+Evidence  │          │ Answer+Evidence   │
       └────────┬─────────┘          └─────────┬────────┘
                └──────────────┬───────────────┘
                               ↓
                    ┌──────────────────────┐
                    │   DIALOGUE MANAGER    │
                    │ intent, context,      │
                    │ coreference ("its")   │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │      EVALUATION       │
                    │ EM / F1 / Accuracy    │
                    └──────────────────────┘
```

Frontend routes: `/`, `/ir-qa`, `/knowledge-qa`, `/chat`, `/evaluation` — each a visually distinct page hitting its own backend endpoint(s).

---

## 3. Academic Explanations

### 3.1 Information Retrieval (`services/retrieval.py`)
- **Corpus**: 8 local `.txt` documents in `data/ir_documents/`, spanning science, history, geography, technology, and education.
- **Preprocessing**: lightweight normalization plus a small abbreviation-expansion step (e.g. "CEO" → "chief executive officer") so short-form questions can still match the corpus's full-form wording.
- **Indexing**: two `TfidfVectorizer` indexes are built — one over whole documents (for passage ranking) and one over individual sentences (for fine-grained evidence selection).
- **Retrieval & ranking**: cosine similarity between the query vector and each document/sentence vector; results are sorted by score (highest first).
- **Relevant passage selection**: the top-ranked document's best-matching sentence is chosen as the evidence sentence for answer extraction.

### 3.2 Factoid Question Answering (`services/qa_service.py`)
- **Extractive QA**: a transparent, rule-based extractor keyed on the question's WH-word (who/when/where/what/how many), rather than a black-box model — this keeps the pipeline fully local and explainable.
- **Answer span extraction**: regex-based proper-noun/date/number extraction from the evidence sentence, with a filter that deprioritizes phrases already named in the question (so "Where was Einstein born?" doesn't just echo "Einstein").
- **Confidence score**: a weighted blend of (a) document-level TF-IDF similarity, (b) extraction-rule confidence, and (c) lexical overlap between question and evidence sentence.
- **Evidence passage**: the exact sentence the answer was extracted from is always returned alongside the answer.

### 3.3 Knowledge-Based QA — Healthcare Domain (`services/knowledge_service.py`)
- **Domain & source**: healthcare. The structured knowledge source is `data/healthcare_knowledge_base.csv` — a real CSV dataset (one row per disease), loaded at startup, matching the "CSV / structured database" tooling suggested for this exercise.
- **Entities**: 15 diseases (Diabetes, Hypertension, Asthma, Migraine, Common Cold, Influenza, Malaria, Tuberculosis, Pneumonia, Anemia, Arthritis, Depression, Insomnia, Obesity, Chickenpox), each with aliases for robust matching (e.g. "flu" → Influenza, "type 2 diabetes" → Diabetes).
- **Relations**: `category`, `symptoms`, `causes`, `treatment`, `specialist`, `prevention` — six relation types per disease, giving 90 queryable entity–relation–value triples total.
- **Structured knowledge / lookup**: the CSV is parsed into an in-memory entity → relations dict, functioning as a minimal knowledge graph; a relation-keyword table maps natural-language phrases ("which doctor", "how to prevent", "what causes", …) to relation names.
- **Database/KG lookup pipeline**: question → entity (disease) detection via alias matching → relation detection (keyword matching, constrained to relations that entity actually has) → CSV-backed triple lookup → templated natural-language sentence.
- **Note**: this is a general-knowledge educational demo, not medical advice — the evaluation page includes a "not medical advice" disclaimer, and the dataset intentionally covers only common, well-documented conditions.

### 3.4 Dialogue Management (`services/dialogue_manager.py`)
- **Intents**: `greeting`, `goodbye`, `help`, `fact_question`, `unknown` (question-type intents are further disambiguated downstream by the KB/IR routing).
- **Conversation state (frame)**: `current_entity`, `previous_question`, `previous_answer`, `detected_intent`, `dialogue_context` — one frame per `session_id`, held in memory.
- **Context / simple coreference**: pronouns (`it`, `its`, `he`, `she`, `they`, `that`) in a follow-up question are substituted with `current_entity` before the question is routed — e.g. "What is its population?" after asking about France becomes "What is France population?" internally.
- **Routing**: each non-greeting/help/goodbye message is tried against the Knowledge Base first (higher precision when it has an answer); if the KB has no answer, it falls back to the IR pipeline.

### 3.5 Evaluation (`services/evaluation.py`)
- **Test dataset**: `data/evaluation_dataset.json` — 17 IR questions, 15 KB questions, 7 dialogue turns (all with gold expected answers/intents).
- **Exact Match (EM)**: normalized string equality between predicted and gold answer.
- **F1**: token-level F1 (used for IR, where partial answer overlap is meaningful).
- **Accuracy**: EM plus a substring-based partial-match fallback (used for KB and dialogue intent, where answers are short atomic values).
- **Computed, not invented**: every number shown in the `/evaluation` page and returned by `/api/evaluation` is produced by actually running the current pipeline against the dataset at request time.
- **Limitations** (real, observed): the extractive QA regex has no true Named-Entity-Recognition, so it can occasionally surface a job title ("Chief Executive Officer") instead of a person's name when both are capitalized in the evidence sentence; and the date extractor takes the first date in a sentence, which can be wrong when a sentence contains multiple dates (e.g. a war's start year vs. its end date). These are the two IR questions that currently fail — kept in the dataset deliberately as a realistic result rather than curating them out.

---

## 4. Sample Interaction (Dialogue with Coreference)

```
User: What are the symptoms of Diabetes?
Assistant: Common symptoms of Diabetes include: Frequent urination,
           increased thirst, fatigue, blurred vision.     [Source: Knowledge Base]

User: What is its treatment?
Assistant: Diabetes is usually treated with: Insulin therapy, metformin,
           diet control, regular exercise.                 [Source: Knowledge Base]
                                                       (coreference: "its" → Diabetes)
```

---

## 5. How This Project Satisfies Exercise 2

| Assignment Requirement | Implementation | File / Module | Demonstration |
|---|---|---|---|
| Retrieve relevant passages for a question | TF-IDF + cosine similarity over documents and sentences | `backend/app/services/retrieval.py` | `/ir-qa` page → "Retrieved Passages" panel with scores |
| Extract factoid answers from text | WH-word-driven rule-based extractive QA | `backend/app/services/qa_service.py` | `/ir-qa` page → "Answer" card + evidence sentence |
| Query structured knowledge sources | Entity/relation detection over a JSON knowledge base | `backend/app/services/knowledge_service.py`, `backend/data/knowledge_base.json` | `/knowledge-qa` page → "Knowledge Lookup" + "Structured Result" panels |
| Handle simple conversational interactions | Frame-based dialogue manager with intents, context, and coreference | `backend/app/services/dialogue_manager.py` | `/chat` page → multi-turn conversation, e.g. "its population" |
| Evaluate answer quality | Real EM / F1 / Accuracy computed against a labeled test set | `backend/app/services/evaluation.py`, `backend/data/evaluation_dataset.json` | `/evaluation` page → metric cards + per-question result tables |
| Working QA/chatbot prototype | Full FastAPI backend + React frontend, tested end-to-end | `backend/`, `frontend/` | Runs locally via `uvicorn` + `npm run dev` |
| Sample question-answer set | 17 IR + 15 KB gold Q/A pairs | `backend/data/evaluation_dataset.json` | Used directly by `/api/evaluation` |
| Dialogue flow / frame design | Documented frame fields + intent set | Section 3.4 above, `dialogue_manager.py` | `/chat` page session state (visible via API response) |
| Evaluation summary | Metric cards, tables, and documented limitations | `/evaluation` page, Section 3.5 above | Live in the UI |

---

## 6. Testing

Manual test cases exercised during development (see terminal verification during build; re-run any of these via `/docs` Swagger UI or `curl`):

**IR**
- Normal factoid question → `"Who developed the theory of relativity?"` → `Albert Einstein`, evidence + 3 ranked passages.
- Irrelevant / no-answer question → `"What is the boiling point of mercury?"` → low-similarity documents, low confidence, honest "no confident answer" if score is ~0.
- Question with multiple relevant documents → `"Who founded Microsoft?"` returns Microsoft doc top-ranked, others ranked lower with visible scores.

**Knowledge Base**
- Known entity + known relation → `"What is the capital of France?"` → `Paris`.
- Unknown entity → `"What is the capital of Mars?"` → `entity: null`, graceful "not found" message, no crash.
- Known entity + unsupported relation → e.g. asking Python's "population" → relation not found for that entity, graceful message.

**Dialogue**
- Greeting → `"Hello"` → `greeting` intent, friendly response.
- Follow-up / context-dependent question → capital question then `"What is its population?"` → correctly resolves to the same entity.
- Reset → `POST /api/chat/reset` clears `current_entity` and history for that session.
- Unknown intent → free-text non-question input → falls through gracefully with a "couldn't find an answer" message instead of erroring.

Errors are handled with HTTP 400 for empty input and try/graceful-fallback logic throughout the dialogue manager and QA services — the API never throws an unhandled exception for a normal question.

---

## 7. Project Structure

```
qa-chatbot-system/
├── backend/            # FastAPI app, services, data, README
├── frontend/            # React + Vite + Tailwind app, README
└── README.md            # this file
```

See `backend/README.md` and `frontend/README.md` for setup details of each half.
