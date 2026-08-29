# Frontend — Intelligent QA & Chatbot System

React + Vite + Tailwind CSS interface with five routes: Home, IR-Based QA, Knowledge-Based QA, Chat, and Evaluation.

## Setup

```bash
cd frontend
npm install
```

## Run (development)

```bash
npm run dev
```

Opens at `http://localhost:5173`. API calls to `/api/*` are proxied to `http://localhost:8000` (see `vite.config.js`) — **make sure the backend is running first**.

## Build for production

```bash
npm run build
npm run preview
```

## Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Home.jsx          # Landing page with the two entry-point cards
│   │   ├── IRQA.jsx          # IR-based QA page
│   │   ├── KnowledgeQA.jsx   # Knowledge-based QA page
│   │   ├── Chat.jsx          # Dialogue / chat page
│   │   └── Evaluation.jsx    # Live metrics dashboard
│   ├── components/
│   │   ├── Navbar.jsx
│   │   └── PipelineSteps.jsx # Reusable pipeline-visualization component
│   ├── services/api.js       # Fetch wrapper for the backend REST API
│   ├── App.jsx                # Route definitions
│   └── main.jsx
├── tailwind.config.js
├── vite.config.js
└── package.json
```
