# 🛡️ ThreatLens AI

**AI-Powered Multi-Agent Cybersecurity Intelligence & Incident Response Platform**

> **Detect. Investigate. Remember. Defend.**

ThreatLens AI is a full-stack Security Operations Center (SOC) platform that uses a five-agent AI pipeline to detect suspicious security events, investigate potential threats, recall previous incidents using persistent memory, recommend defensive actions, and learn from analyst-confirmed outcomes.

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Agent Pipeline](#agent-pipeline)
- [Investigation Workflow](#investigation-workflow)
- [API Reference](#api-reference)
- [Database](#database)
- [Demo Walkthrough](#demo-walkthrough)
- [Security Notes](#security-notes)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)

---

## Architecture

```text
┌────────────────────────────────────────────────────────────┐
│                       ThreatLens AI                         │
│                                                            │
│  Frontend (React + Vite)        Backend (FastAPI)          │
│  ┌────────────────────┐        ┌──────────────────────┐    │
│  │ Overview Dashboard │◄──────►│ /api/upload          │    │
│  │ Investigate Threat │        │ /api/investigate     │    │
│  │ Incidents List     │        │ /api/incidents       │    │
│  │ Memory Explorer    │        │ /api/memory          │    │
│  │ Learning Analytics │        │ /api/analytics       │    │
│  └────────────────────┘        └──────────┬───────────┘    │
│                                           │                │
│             ┌─────────────────────────────▼─────────────┐  │
│             │              5-Agent Pipeline              │  │
│             │                                            │  │
│             │  1. Threat Detection                       │  │
│             │  2. Investigation                          │  │
│             │  3. Hindsight Memory                       │  │
│             │  4. Response Recommendations               │  │
│             │  5. Learning                               │  │
│             └────────────────────────────────────────────┘  │
│                                                            │
│  Persistent Storage                                         │
│  ┌────────────────────┐    ┌───────────────────────────┐   │
│  │ MongoDB            │    │ Hindsight Memory Bank     │   │
│  │ Incidents          │    │ Retain / Recall / Reflect │   │
│  │ Events             │    │ Historical threat context │   │
│  │ Feedback           │    │                           │   │
│  └────────────────────┘    └───────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, React Router, Axios, Recharts, Lucide React |
| Backend | Python 3.11+, FastAPI, Pydantic, Uvicorn |
| LLM Inference | Groq API (`openai/gpt-oss-120b`) with deterministic fallback |
| Persistent Memory | Hindsight SDK (`hindsight-client==1.2.0`) |
| Database | MongoDB 8.x, Motor async driver |
| Storage Fallback | Embedded JSON storage |

---

## Prerequisites

| Requirement | Minimum Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| MongoDB | 7.0+ |
| Groq API Key | Required for LLM inference |
| Hindsight API Key | Required for persistent memory |

Useful resources:

- [Python](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/)
- [MongoDB](https://www.mongodb.com/try/download/community)
- [Groq Console](https://console.groq.com/)
- [Hindsight](https://hindsight.vectorize.io/)

**Important:** MongoDB should be running locally if you want to use MongoDB storage. If MongoDB is unavailable, the application can fall back to embedded JSON storage.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Ramithagolla/Dynamic-kicks.git
cd Dynamic-kicks
```

### 2. Configure environment variables

Copy the example environment file:

```bash
copy .env.example .env
```

Open `.env` and add your API credentials.

### 3. Install backend dependencies

From the project root:

```bash
python -m pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Start the application

**Windows:**

Open two terminals in the project root.

Terminal 1 — Backend:

```bash
run_backend.bat
```

Terminal 2 — Frontend:

```bash
run_frontend.bat
```

**Manual startup:**

Terminal 1 — Backend:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Run the backend command from the `backend` directory.

Terminal 2 — Frontend:

```bash
cd frontend
npm run dev
```

### 6. Open the application

| Service | URL |
|---|---|
| Frontend Dashboard | http://localhost:5173 |
| Backend API | http://127.0.0.1:8000 |
| Interactive API Docs | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/health |

---

## Configuration

All credentials should be configured in the root `.env` file.

**Never commit your `.env` file or expose API keys publicly.**

### Environment Variables

```env
# Application
APP_NAME=ThreatLens AI
ENVIRONMENT=development
PORT=8000
DEBUG=True

# Groq API
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b

# Hindsight Persistent Memory
HINDSIGHT_API_KEY=your_hindsight_api_key
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_BANK_ID=threatlens-security-memory

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=threatlens_db
```

### Getting API Keys

**Groq API**

1. Visit [Groq Console](https://console.groq.com/).
2. Create an account.
3. Navigate to API Keys.
4. Generate an API key and configure `GROQ_API_KEY`.

**Hindsight**

1. Visit [Hindsight](https://hindsight.vectorize.io/).
2. Create an account.
3. Generate an API key.
4. Configure `HINDSIGHT_API_KEY`.

The memory bank ID used by the application is:

```text
threatlens-security-memory
```

### Fallback Behavior

| Service | Fallback Behavior |
|---|---|
| Groq | Deterministic rule-based processing when the API is unavailable |
| Hindsight | Reports unsuccessful memory operations rather than pretending memory was stored |
| MongoDB | Embedded JSON storage when MongoDB is unreachable |

---

## Agent Pipeline

ThreatLens AI consists of five specialized agents.

| Agent | Responsibility |
|---|---|
| Agent 1 — Threat Detection | Analyzes uploaded security logs, identifies suspicious activity, and assigns severity levels. |
| Agent 2 — Investigation | Builds incident timelines, separates observed facts from hypotheses, and identifies attack patterns. |
| Agent 3 — Memory | Uses Hindsight recall and reflect to retrieve and synthesize historical incident knowledge. |
| Agent 4 — Response Recommendations | Generates prioritized defensive recommendations informed by investigation findings and historical context. |
| Agent 5 — Learning | Uses Hindsight retain to preserve verified incident knowledge after analyst confirmation. |

### Five-Agent Workflow

```text
Security Log Upload
        |
        v
1. Threat Detection
        |
        v
2. Investigation
        |
        v
3. Hindsight Memory
   Recall + Reflect
        |
        v
4. Response Recommendations
        |
        v
Human Analyst Review
        |
        v
5. Learning
   Hindsight Retain
        |
        v
Future Investigations
```

---

## Investigation Workflow

1. The analyst uploads CSV or JSON security logs.
2. The backend validates and normalizes the uploaded data.
3. Agent 1 detects suspicious activity using security rules and LLM interpretation.
4. Agent 2 creates an investigation report with an event timeline, facts, hypotheses, and attack patterns.
5. Agent 3 retrieves relevant historical information using Hindsight recall and reflect.
6. Agent 4 generates prioritized defensive recommendations.
7. The frontend displays the investigation results.
8. The analyst reviews and confirms the findings.
9. Agent 5 retains verified incident knowledge through Hindsight.
10. Future investigations can recall relevant historical knowledge.

**Human approval is required:** Recommended security actions are advisory. The system does not automatically execute remediation actions.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks service health |
| POST | `/api/upload` | Uploads CSV/JSON security logs |
| POST | `/api/investigate` | Executes the five-agent investigation |
| GET | `/api/incidents` | Lists incidents |
| GET | `/api/incidents/{id}` | Retrieves incident details |
| POST | `/api/incidents/{id}/feedback` | Submits analyst feedback |
| GET | `/api/memory/search?query=...` | Searches Hindsight memory |
| GET | `/api/memory/list` | Lists recent memory entries |
| GET | `/api/analytics/summary` | Retrieves incident analytics |

Interactive API documentation:

http://localhost:8000/docs

---

## Database

### MongoDB Collections

| Collection | Purpose |
|---|---|
| `incidents` | Incident records and investigation results |
| `events` | Individual security events linked to incidents |
| `feedback` | Analyst feedback and confirmed resolutions |

### Hindsight Memory Bank

**Bank ID:** `threatlens-security-memory`

Hindsight stores verified incident knowledge, including:

- Confirmed root causes
- Effective remediation actions
- Accepted and rejected recommendations
- Resolution context and notes

MongoDB stores structured incident records, while Hindsight provides persistent semantic memory that can be recalled and synthesized across future investigations.

---

## Demo Walkthrough

### Step 1 — Upload Security Logs

1. Open the dashboard at http://localhost:5173.
2. Navigate to **Investigate Threat**.
3. Upload a supported CSV or JSON security log.
4. Click **Run Investigation**.

### Step 2 — Review Investigation Results

The investigation produces:

- Threat summary and severity
- Attack indicators
- Event timeline
- Observed facts and hypotheses
- Historical memory results
- Prioritized response recommendations

### Step 3 — Confirm and Learn

1. Review the investigation findings.
2. Navigate to the Incidents view.
3. Confirm the incident.
4. Provide root-cause and resolution information.
5. Submit the analyst feedback.

The Learning Agent uses verified information to retain incident knowledge in Hindsight.

### Step 4 — Test Memory Recall

Upload a similar security incident and run another investigation.

The Memory Agent can retrieve relevant historical knowledge and provide context for the new investigation.

### Step 5 — Explore Memory

Navigate to **Memory Explorer** to inspect retained knowledge, search historical information, and view memory synthesis.

---

## Security Notes

- **Credential protection:** API keys are stored in `.env`, which should never be committed.
- **Human approval:** Response recommendations require analyst approval.
- **Transparent fallbacks:** Unavailable services are reported honestly.
- **Evidence-based learning:** Only analyst-confirmed information is retained as verified incident knowledge.
- **No automatic remediation:** Defensive recommendations are advisory and are not automatically executed.

---

## Running Tests

Run the following commands from the project root:

```bash
# Comprehensive pipeline audit
python backend/tests/test_audit_suite.py

# End-to-end pipeline test
python backend/tests/test_e2e_full.py

# Unit pipeline test
python backend/tests/test_pipeline.py
```

---

## Project Structure

```text
Dynamic-kicks/
│
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── run_backend.bat
├── run_frontend.bat
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── agents/
│   │   │   ├── detection_agent.py
│   │   │   ├── investigation_agent.py
│   │   │   ├── memory_agent.py
│   │   │   ├── response_agent.py
│   │   │   └── learning_agent.py
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── models/
│   │   └── services/
│   │       ├── mongo_service.py
│   │       ├── hindsight_service.py
│   │       └── llm_service.py
│   ├── sample_data/
│   └── tests/
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   ├── components/
    │   ├── api/
    │   └── App.jsx
    ├── package.json
    └── vite.config.js
```

---

## Project Information

**Project:** ThreatLens AI

**Tagline:** Detect. Investigate. Remember. Defend.

**Repository:** https://github.com/Ramithagolla/Dynamic-kicks

**Built with:** React, FastAPI, Groq, Hindsight, and MongoDB.

