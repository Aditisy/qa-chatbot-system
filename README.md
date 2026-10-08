# Intelligent QA and Chatbot System - Lab Exercise 2

Aditi S Yaranal | 1GA23AI003 | 7th Semester, AIML
Global Academy of Technology | Advance NLP AML23702 | 8 October 2026

## Features
- IR factoid QA: TF-IDF document/sentence ranking, rule-based span extraction, evidence and source.
- Structured QA: 15 disease entities with six relations in healthcare_knowledge_base.csv.
- Dialogue: intents, per-tab sessions, healthcare pronoun follow-ups and reset.
- Live evaluation: 17 IR examples, 15 KB examples and seven dialogue turns.

## Run locally (Windows PowerShell)
Requires Python 3.12 and Node.js/npm. No LLM account or API key is required.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -r backend/requirements.txt
.\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```
In a second terminal:
```powershell
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```
Open http://127.0.0.1:5173; API documentation: http://127.0.0.1:8000/docs.

## Verify
```powershell
.\.venv\Scripts\python -m pip install -r backend/requirements-dev.txt
$env:PYTHONPATH='backend'
.\.venv\Scripts\python -m unittest discover -s tests -v
cd frontend
npm run build
```
For evaluation, visit the Evaluation page or GET /api/evaluation.

## Results and analysis
Recorded on 8 October 2026. Nine regression/API tests and frontend build passed.
IR exact match improved from 14/17 (82.4%) to 17/17; token F1 from 85.7% to 100%.
KB expected-fact coverage is 15/15, dialogue intent 7/7 and entity state 4/4.
These are small development sets used during debugging, not held-out benchmarks.
KB coverage requires the complete expected phrase within the longer answer;
it does not establish medical validity. Confidence is a heuristic, not a probability.

The review fixed compound person extraction, role subjects, begin/end evidence,
source attribution, alias boundaries, unsupported relations and context leakage.
Evaluation now uses strict IR exact-match correctness, one-way KB phrase coverage
and explicit dialogue entity checks. See output/evaluation_before.json,
output/evaluation_after.json and output/regression_results.txt.

The healthcare CSV is an educational sample without per-row clinical provenance.
Its responses are not medical advice. The corpus is static; rule-based QA can fail
on paraphrases, unsupported relations, multi-date sentences and unfamiliar entities.
Session state is in memory without persistence or expiry; use as a local demo.

Compatible npm updates were applied. npm audit still reports 11 advisories
(5 moderate, 6 high), requiring a separately tested major-version migration.
The current project is not production-hardened; bind development servers locally.

## Deliverables
- [Lab 2 report](output/pdf/1GA23AI003_Exp2_QA_Chatbot_System.pdf)
- [Readable report](REPORT.md)
- [Dialogue flow and frame](docs/dialogue_flow.md)
- [Sample QA set](backend/data/evaluation_dataset.json)
- [Evaluation evidence](output/evaluation_after.json)

To rebuild the PDF, install reportlab and pillow, then run python scripts/build_report.py.
Source corpus, CSV and evaluation questions are included; dependencies and local
runtime files are excluded. This repository contains Exercise 2 only.
