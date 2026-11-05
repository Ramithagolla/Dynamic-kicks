# 🛡️ ThreatLens AI

**AI-Powered Multi-Agent Cybersecurity Intelligence & Incident Response Platform**

> **Detect. Investigate. Remember. Defend.**

ThreatLens AI is a full-stack hackathon-ready Security Operations Center (SOC) platform that uses a five-agent AI pipeline to detect suspicious security events, investigate potential threats, recall previous incidents from persistent memory, recommend defensive actions, and learn from analyst-confirmed outcomes.

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

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ThreatLens AI                        │
│                                                         │
│  Frontend (React + Vite)         Backend (FastAPI)      │
│  ┌────────────────────┐         ┌──────────────────┐    │
│  │ Overview Dashboard  │◄───────►│  /api/upload     │    │
│  │ Investigate Threat  │         │  /api/investigate│    │
│  │ Incidents List      │         │  /api/incidents  │    │
│  │ Memory Explorer     │         │  /api/memory     │    │
│  │ Learning Analytics  │         │  /api/analytics  │    │
│  └────────────────────┘         └────────┬─────────┘    │
│                                          │               │
│           ┌──────────────────────────────▼────────────┐  │
│           │          5-Agent Pipeline                  │  │
│           │                                            │  │
│           │  Agent 1: Threat Detection                 │  │
│           │    ↓ (rule-based + LLM)                   │  │
│           │  Agent 2: Investigation                    │  │
│           │    ↓ (timeline, facts, hypotheses)         │  │
│           │  Agent 3: Memory (Hindsight recall/reflect)│  │
│           │    ↓ (historical context injection)        │  │
│           │  Agent 4: Response Recommendations         │  │
│           │    ↓ (memory-informed, human-approved)     │  │
│           │  Agent 5: Learning (Hindsight retain)      │  │
│           └────────────────────────────────────────────┘  │
│                                                         │
│  Persistent Storage                                      │
│  ┌─────────────────┐    ┌──────────────────────────┐   │
│  │  MongoDB 8.x    │    │  Hindsight Memory Bank   │   │
│  │  - incidents    │    │  threatlens-security-     │   │
│  │  - events       │    │  memory                  │   │
│  │  - feedback     │    │  (retain/recall/reflect)  │   │
│  └─────────────────┘    └──────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, Tailwind CSS, React Router, Axios, Recharts, Lucide React |
| **Backend** | Python 3.11+, FastAPI, Pydantic, Uvicorn |
| **LLM Inference** | Groq API (`openai/gpt-oss-120b`) with deterministic fallback |
| **Persistent Memory** | Hindsight SDK (`hindsight-client==1.2.0`) — retain, recall, reflect |
| **Database** | MongoDB 8.x (motor async driver); embedded JSON fallback if unavailable |

---

## Prerequisites

| Requirement | Minimum Version | Notes |
|-------------|----------------|-------|
| Python | 3.11+ | 3.14 tested |
| Node.js | 18+ | 20 LTS recommended |
| MongoDB | 7.0+ | 8.x running locally at `localhost:27017` |
| Groq API key | — | [console.groq.com](https://console.groq.com) |
| Hindsight API key | — | [hindsight.vectorize.io](https://hindsight.vectorize.io) |

> [!IMPORTANT]
> MongoDB must be installed and running locally (`mongod`). If MongoDB is unavailable, the app falls back to embedded JSON storage — clearly labeled in `/health`.

---

## Quick Start

### 1. Clone or download the project

```bash
git clone <repo-url> "ThreatLens AI"
cd "ThreatLens AI"
```

### 2. Configure credentials

```bash
cp .env.example .env
# Edit .env with your actual API keys (see Configuration section)
```

### 3. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Start both servers

**Windows (double-click or run):**
```cmd
run_backend.bat    # Starts FastAPI on http://localhost:8000
run_frontend.bat   # Starts Vite on http://localhost:5173
```

**Manual:**
```bash
# Terminal 1 — Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

### 6. Verify health

```bash
curl http://localhost:8000/health
```

Expected output (with valid credentials):
```json
{
  "status": "healthy",
  "mongodb": { "status": "connected", "mode": "mongodb" },
  "hindsight": { "status": "connected", "bank_id": "threatlens-security-memory" },
  "groq": { "status": "connected", "model": "openai/gpt-oss-120b" },
  "agents": {
    "agent_1_detection": "active",
    "agent_2_investigation": "active",
    "agent_3_memory": "active",
    "agent_4_response": "active",
    "agent_5_learning": "active"
  }
}
```

---

## Configuration

All credentials are stored in `.env` at the project root. **Never commit `.env` to source control.**

### `.env` file

```env
# Application
APP_NAME=ThreatLens AI
ENVIRONMENT=development
PORT=8000
DEBUG=True

# Groq API — LLM inference for all 5 agents
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=openai/gpt-oss-120b

# Hindsight Persistent Memory — retain / recall / reflect
HINDSIGHT_API_KEY=hsk_your_key_here
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_BANK_ID=threatlens-security-memory

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=threatlens_db
```

### Getting API Keys

**Groq:**
1. Go to [console.groq.com](https://console.groq.com)
2. Create an account → API Keys → Create new key
3. Available models for free tier: `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`

**Hindsight:**
1. Go to [hindsight.vectorize.io](https://hindsight.vectorize.io)
2. Create an account → API Keys
3. The bank `threatlens-security-memory` is created automatically on first startup

### Fallback Behavior

| Service | Missing Credential | Behavior |
|---------|--------------------|----------|
| Groq | No `GROQ_API_KEY` | Deterministic rule-based engine activates — still produces security findings |
| Hindsight | No `HINDSIGHT_API_KEY` | Memory operations return `success: false` with clear error — no simulation |
| MongoDB | Unreachable | Falls back to embedded JSON storage at `backend/data/db_store/` |

---

## Agent Pipeline

| Agent | Role | Technology |
|-------|------|-----------|
| **Agent 1 — Threat Detection** | Analyzes uploaded security logs, applies deterministic rules (brute-force thresholds, compromise indicators) + LLM interpretation. Assigns severity: Critical / High / Medium / Low. | Groq LLM + Rule Engine |
| **Agent 2 — Investigation** | Generates incident report with event timeline, observed facts vs. hypotheses, attack pattern mapping (MITRE ATT&CK), confidence score. | Groq LLM |
| **Agent 3 — Memory** | Calls Hindsight `recall` to retrieve past similar incidents, then `reflect` to synthesize historical patterns. Displays actual retrieved memories and their references. | Hindsight SDK |
| **Agent 4 — Response Recommendations** | Generates prioritized defensive actions informed by current evidence and retrieved historical memories. All actions require human approval — none are executed automatically. | Groq LLM + Hindsight context |
| **Agent 5 — Learning** | On analyst confirmation, calls Hindsight `retain` to store verified incident facts, root causes, and effective remediations. Rejects unverified AI assumptions. | Hindsight SDK |

---

## Investigation Workflow

```
1. Analyst uploads CSV or JSON security logs (enforcing max 100 MB / 104,857,600 bytes)
         ↓
2. Backend validates, normalizes fields (timestamp, source_ip, username, status, etc.),
   and discards invalid placeholder rows (e.g., "No Data to export") with clear counts
         ↓
3. Agent 1: Threat Detection
   • Apply deterministic security rules (brute-force thresholds, privilege anomalies)
   • For zero-failure benign logs: classifies as "Normal Activity / Baseline" (Severity: Low)
   • LLM interprets rule findings for attack pattern categorization & MITRE ATT&CK mapping
         ↓
4. Agent 2: Investigation
   • Build chronological event timeline
   • Distinguish observed facts from evidence-based hypotheses
         ↓
5. Agent 3: Memory — Genuine Hindsight recall() & reflect()
   • Search historical incidents matching current threat indicators and attack type
   • Synthesize past containment protocols & resolutions
   • If no matching history or baseline traffic: truthfully reports "no_matching_memory"
         ↓
6. Agent 4: Response Recommendations
   • Formulate prioritized defensive containment & eradication recommendations
   • All actions require explicit human approval (never executed automatically)
         ↓
7. Frontend displays interactive SOC Investigation Result Card (15 real data fields)
         ↓
8. Analyst reviews findings, confirms root cause and accepted actions
         ↓
9. Agent 5: Learning — Genuine Hindsight retain()
   • Persist verified incident facts, root causes, and containment outcomes into Hindsight
   • Rejects unverified AI hallucinations or assumptions
         ↓
10. Future investigations on similar attacks automatically recall and apply this intelligence
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health (MongoDB, Hindsight, Groq, agents) |
| `POST` | `/api/upload` | Upload CSV/JSON security logs |
| `POST` | `/api/investigate` | Run 5-agent investigation pipeline |
| `GET` | `/api/incidents` | List all incidents |
| `GET` | `/api/incidents/{id}` | Get single incident details |
| `POST` | `/api/incidents/{id}/feedback` | Submit analyst feedback (triggers learning) |
| `GET` | `/api/memory/search?query=...` | Search Hindsight memory bank |
| `GET` | `/api/memory/list` | List recent memory entries |
| `GET` | `/api/analytics/summary` | Incident statistics and learning analytics |

**Interactive API docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Database

### MongoDB Collections

| Collection | Purpose |
|------------|---------|
| `incidents` | Incident records with investigation results, severity, status |
| `events` | Individual log events linked to incidents |
| `feedback` | Analyst feedback and confirmed resolutions |

### Hindsight Memory Bank

**Bank ID:** `threatlens-security-memory`

Stores verified, analyst-confirmed incident knowledge:
- Confirmed root causes
- Effective remediation actions
- Accepted and rejected recommendations
- Resolution context and notes

The Hindsight memory bank supplements MongoDB: MongoDB stores structured incident records; Hindsight stores semantic knowledge that can be recalled and synthesized across future investigations.

### Storage Mode Transparency

The `/health` endpoint always reports the actual storage mode:
- `"mode": "mongodb"` — Real MongoDB is in use
- `"mode": "embedded-json-storage"` — MongoDB is unreachable; JSON files at `backend/data/db_store/` are in use

---

## Demo Walkthrough

### Step 1 — Upload a Security Log

1. Open [http://localhost:5173](http://localhost:5173)
2. Navigate to **Investigate Threat** in the sidebar
3. Upload `backend/sample_data/incident_1_initial_brute_force.csv`
4. Click **Run Investigation**

### Step 2 — Review the Investigation

The 5-agent pipeline produces:
- **Threat Summary** — severity, attack type, indicators
- **Event Timeline** — chronological attack progression
- **Observed Facts vs. Hypotheses** — clearly separated
- **Memory Agent Results** — Hindsight recall results (empty on first run)
- **Response Recommendations** — prioritized actions (all require human approval)

### Step 3 — Confirm and Learn

1. Review the recommendations
2. Click **Confirm Incident** in the Incidents view
3. Fill in root cause and resolution notes
4. Submit — Agent 5 retains knowledge to Hindsight

### Step 4 — Test Memory Recall

1. Upload `backend/sample_data/incident_2_similar_credential_stuffing.csv`
2. Click **Run Investigation**
3. The **Memory Agent** section now shows retrieved memories from Incident 1
4. Recommendations are informed by historical evidence

### Step 5 — Explore Memory

Navigate to **Memory Explorer** to:
- Search the Hindsight memory bank
- See retained incident knowledge
- View reflect synthesis

---

## Security Notes

- **Credentials** — All API keys are stored in `.env` only. `.gitignore` excludes `.env` from source control.
- **No auto-remediation** — Agent 4 recommendations are advisory only; no automated actions are taken.
- **No fabrication** — If Groq or Hindsight are unavailable, the system uses deterministic fallbacks and reports status honestly.
- **No credential exposure** — API keys are never logged or returned in API responses. Errors redact keys if they appear in exception messages.
- **Human approval required** — All recommended security actions are marked `requires_human_approval: true`.

---

## Running Tests

```bash
# Comprehensive pipeline audit suite (100MB limit, junk rejection, Incident 1, Hindsight Retain, Incident 2 Recall, Baseline classification, MongoDB persistence)
python backend/tests/test_audit_suite.py

# End-to-end pipeline test
python backend/tests/test_e2e_full.py

# Unit pipeline test
python backend/tests/test_pipeline.py
```

---

## Project Structure

```
ThreatLens AI/
├── .env                          # Credentials (not in source control)
├── .env.example                  # Template — copy to .env
├── .gitignore
├── README.md
├── run_backend.bat               # Windows: start backend
├── run_frontend.bat              # Windows: start frontend
│
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app, CORS, lifespan
│   │   ├── config.py             # Settings from .env
│   │   ├── agents/               # 5 agent implementations
│   │   │   ├── detection_agent.py
│   │   │   ├── investigation_agent.py
│   │   │   ├── memory_agent.py
│   │   │   ├── response_agent.py
│   │   │   └── learning_agent.py
│   │   ├── api/routes/           # FastAPI route handlers
│   │   ├── models/schemas.py     # Pydantic models
│   │   ├── prompts/              # LLM prompt files
│   │   └── services/
│   │       ├── mongo_service.py  # MongoDB (real + embedded fallback)
│   │       ├── hindsight_service.py  # Hindsight retain/recall/reflect
│   │       └── llm_service.py    # Groq LLM + deterministic fallback
│   ├── sample_data/              # Synthetic incident CSV/JSON
│   ├── tests/                    # E2E and unit tests
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── pages/                # React pages (Overview, Investigate, etc.)
    │   ├── components/           # Reusable UI components
    │   ├── api/                  # Axios API client
    │   └── App.jsx
    ├── package.json
    └── vite.config.js
```
