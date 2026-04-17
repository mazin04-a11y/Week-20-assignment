# 🤖 AIOps Mission Dashboard — Blueprint Blue

> **20-Week AI Agentic Systems Bootcamp | Week 18 Capstone**
> A production-grade, multi-agent AI service implementing the full R-A-R Pipeline (Research → Analyse → Report) with a 4-layer Resilience Stack, Semantic Memory, and a CI/CD deployment pipeline.

---

## 🗺️ What Is This?

This project is a **Blueprint Blue** deployment of the R-A-R Pipeline — the capstone architecture from the AI Agentic Systems bootcamp. It transitions from "Sage Green" (a local script) to a **fully deployed, containerised, CI/CD-backed service**.

Three specialist AI agents collaborate in a hierarchical orchestration:

```
User Query
    │
    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Researcher  │────▶│   Analyst   │────▶│   Writer    │
│  (Phase 1)   │     │  (Phase 2)  │     │  (Phase 3)  │
│ Web + Vault  │     │ SQL + Facts │     │  Markdown   │
└─────────────┘     └─────────────┘     └─────────────┘
    │                     │                    │
    ▼                     ▼                    ▼
SerperDevTool       SafeQueryTool        FileWriteTool
WebScraperTool      FileReadTool         ContextWriterTool
FileReadTool        (memory.db)          (context_notes.txt)
```

A **Manager Agent** (GPT-4o) oversees the entire pipeline via `Process.hierarchical`.

---

## 📁 Week 18 Blueprint Blue Structure

```
Docker and Jenkins/
├── src/
│   ├── crew.py                    ← Core orchestration (Stage 1–5)
│   ├── agents/
│   │   └── research_agents.py    ← Deep Role Engineering (Weeks 4/11/14)
│   ├── tasks/
│   │   └── research_tasks.py     ← R-A-R Task chain (Week 9 context chaining)
│   └── tools/
│       ├── custom_tools.py       ← SafeQueryTool, WebScraperTool, ContextWriterTool
│       ├── database.py           ← SQLite memory.db Hard Drive (Week 14)
│       ├── resilience.py         ← 4-Layer Resilience Stack (Week 15)
│       └── debug_tools.py        ← Smoke Test, ExecutionTracer, Go-Live (Weeks 14/16/18)
├── config/
│   ├── agents.yaml               ← Agent personas — separated from code (Week 18)
│   └── tasks.yaml                ← Task instructions with {user_topic} placeholder
├── app/
│   ├── streamlit_app.py          ← AIOps Mission Dashboard (Week 17)
│   └── main.py                   ← FastAPI backend — /kickoff + /health (Week 17)
├── tests/
│   └── test_crew.py              ← Compliance tests (Week 18)
├── .env.example                  ← API key template (ID Badge Protocol)
├── .env                          ← NEVER committed — gitignored
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── Dockerfile                    ← Python 3.12-slim container
├── docker-compose.yml            ← Jenkins + app services
└── Jenkinsfile                   ← CI/CD pipeline: Install → Test → Build → Push
```

---

## 🏗️ Architecture Patterns by Week

Every file in this project implements patterns explicitly taught in the course:

| Week | Pattern | Where Used |
|------|---------|------------|
| Week 1–3 | **ID Badge Protocol** — `.env` only, never hardcoded | All files, `.env.example` |
| Week 4 | **Deep Role Engineering** — Role / Goal / Backstory | `config/agents.yaml`, `research_agents.py` |
| Week 5 | **Task Orchestration** — `description` + `expected_output` | `config/tasks.yaml` |
| Week 7 | **Custom Tools** — `BaseTool` with `_run()` | `custom_tools.py` |
| Week 9 | **Context Chaining** — `context=[prev_task]` | `research_tasks.py`, `crew.py` |
| Week 10 | **Glass Box Experience** — `verbose=True`, thought tracing | All agents |
| Week 11 | **SerperDevTool** — web search integration | `crew.py` (Researcher) |
| Week 13 | **Process.hierarchical** — Manager Agent oversight | `crew.py` |
| Week 14 | **Semantic Memory** — `memory=True` + embedder | `crew.py` |
| Week 14 | **SQLite Hard Drive** — `memory.db` persistent facts | `database.py` |
| Week 14 | **Schema in Backstory** — prevents hallucinated column names | `research_agents.py` |
| Week 14 | **Execution Tracer** — timing, tool usage, decision flow | `debug_tools.py` |
| Week 15 | **Resilience Stack** — 4-layer Defense in Depth | `resilience.py` |
| Week 16 | **Smoke Test** — environment diagnostics table | `debug_tools.py` |
| Week 17 | **Streamlit UI** — `st.form`, `st.spinner`, `st.session_state` | `streamlit_app.py` |
| Week 17 | **FastAPI Interface** — `/kickoff`, `/history`, `/health` | `main.py` |
| Week 18 | **YAML Config Isolation** — personas separate from engine | `config/` directory |
| Week 18 | **Go-Live Checklist** — pre-deployment verification | `debug_tools.py` |

---

## 🛡️ Resilience Stack (Week 15 — Defense in Depth)

The system is **antifragile** — it gets more robust under pressure:

```
Layer 1 — Exponential Backoff + Jitter
    • Retries API calls up to 3 times
    • Wait: 2^attempt + random(0–1)s to prevent Thundering Herd
    • Handles: 503 errors, timeouts, API instability

Layer 2 — Budgetary Caps (Denial of Wallet Prevention)
    • max_tokens = 5,000 per agent call (hard limit)
    • Rejects queries > 2,000 characters at input
    • Prevents: runaway costs, infinite reasoning loops

Layer 3 — JSON Schema Enforcement (Structural Integrity)
    • Task(output_json=StructuredReport) on analysis task
    • Pydantic model: title, summary, findings, sources, status
    • Converts non-deterministic LLM output → reliable structured data

Layer 4 — Reviewer Agent (Semantic Integrity / Metacognition)
    • Dedicated Quality Reviewer critiques every draft
    • Flags hallucinated citations, unsupported claims
    • self_correction_loop() — max 3 iterations before fallback
    • Prevents: Hallucination Cascade
```

---

## 🗄️ Memory Architecture (Week 14)

Two memory types work together as the agent's "brain":

**Relational Memory (Hard Drive) — `memory.db`:**
```sql
research_findings  (id, topic, content, source_url, created_at)
run_history        (id, user_topic, result, status, created_at)
knowledge_items    (id, key, value, category, created_at)
```
→ Stores structured facts, run history, audit trail. Queried by `SafeQueryTool`.

**Semantic Memory (Embedding Layer) — CrewAI built-in:**
```python
Crew(memory=True, embedder={"provider": "openai", "config": {"model": "text-embedding-3-small"}})
```
→ Stores agent interactions as embeddings. Retrieves relevant past context using cosine similarity (threshold > 0.75).

---

## 🔒 Safety Guardrails

**SafeQueryTool** enforces read-only database access (Layer 2 Guardrail):
```python
# Blocks any destructive SQL — no DROP, DELETE, UPDATE, or INSERT
if any(k in query.upper() for k in ['DROP','DELETE','UPDATE','INSERT']):
    raise ValueError("Action Prohibited: Read Only Access")
```

**ID Badge Protocol:**
- All API keys stored in `.env` only
- `.env` is gitignored — never committed
- `.env.example` provides template with placeholder values

---

## ⚙️ Setup — Local Development

### Prerequisites
- Python 3.12+
- Docker Desktop (for Jenkins CI/CD)
- API keys: OpenAI, Anthropic, Serper

### 1. Clone & Configure

```bash
git clone https://github.com/mazin04-a11y/Docker-and-Jenkins.git
cd "Docker and Jenkins"

# Copy the template and fill in your keys
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
SERPER_API_KEY=your_serper_key
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Environment (Smoke Test — Week 16)

```bash
python src/tools/debug_tools.py
```

This runs the **Environment Diagnostics Table** — checks Python version, API keys, required files, DB access, and core imports. Fix any ❌ FAIL items before proceeding.

### 4. Run the Pipeline

**Streamlit UI (AIOps Mission Dashboard):**
```bash
streamlit run app/streamlit_app.py
```
→ Opens at http://localhost:8501

**FastAPI Backend:**
```bash
uvicorn app.main:app --reload
```
→ API docs at http://localhost:8000/docs

**Direct crew run:**
```bash
python src/crew.py
```

### 5. Run Tests

```bash
pytest tests/ -v
```

---

## 🐳 Docker + Jenkins CI/CD (Week 18)

### Start Jenkins

```bash
docker compose up -d
```

- **Jenkins** → http://localhost:8080
- **App** → http://localhost:8501 (Streamlit), http://localhost:8000 (FastAPI)

Jenkins runs **inside Docker** with the Docker socket mounted — it can build and push Docker images as part of the CI pipeline.

### Jenkinsfile Pipeline Stages

```
Stage 1: Checkout     ← Pull latest code from GitHub
Stage 2: Install      ← pip install -r requirements.txt
Stage 3: Test         ← pytest tests/ (must pass to continue)
Stage 4: Docker Build ← docker build -t aiops-mission-dashboard .
Stage 5: Push         ← git push origin main → triggers Streamlit Cloud
```

### Go-Live Checklist (Week 18)

Before deploying, run:
```bash
python -c "from src.tools.debug_tools import run_golive_checklist; run_golive_checklist()"
```

Checks: modular structure intact, secrets protected, requirements.txt present, README present.

---

## 🚀 Streamlit Cloud Deployment

The CI/CD flow from local to production:

```
Local Dev  →  git push  →  Jenkins Tests  →  GitHub  →  Streamlit Cloud
```

1. Connect your GitHub repo at [share.streamlit.io](https://share.streamlit.io)
2. Set main file: `app/streamlit_app.py`
3. Add secrets in Streamlit Cloud dashboard (same keys as `.env`)
4. Every `git push` triggers automatic redeployment

---

## 🔬 Debugging (Glass Box Experience — Week 10/16)

**Debug Mode in UI:** Toggle "🔬 Debug Mode" in the sidebar to expose:
- Session state inspection (run count, last topic, result status)
- Environment variables status (API keys set/missing)
- Raw last result output

**Execution Trace (Week 14):**
Every crew run prints a timestamped trace to console:
```
══════════════════════════════════════════════════════════
  EXECUTION TRACE (Week 14 — Decision Flow)
══════════════════════════════════════════════════════════
  [  1.23s] Senior Research Specialist   → Searching web for topic
             🔧 Tool: SerperDevTool
  [  8.45s] Data Analyst                 → Querying memory.db
             🔧 Tool: SafeQueryTool
  [ 12.67s] Report Writer               → Writing final report
──────────────────────────────────────────────────────────
  Total elapsed : 15.2s
  Final status  : SUCCESS
══════════════════════════════════════════════════════════
```

**Mission Log:** Persistent log file at `mission_log.txt` captures all retry attempts, budget cap warnings, and pipeline events.

---

## 📚 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Agent Framework | CrewAI | Multi-agent orchestration |
| LLM (Manager) | GPT-4o | Hierarchical oversight |
| LLM (Workers) | GPT-4o | Research, Analysis, Writing |
| Embeddings | text-embedding-3-small | Semantic memory retrieval |
| Web Search | SerperDevTool | Real-time web research |
| UI | Streamlit | AIOps Mission Dashboard |
| API | FastAPI + Uvicorn | Backend REST interface |
| Database | SQLite (memory.db) | Relational memory / audit trail |
| Config | YAML (agents + tasks) | Persona / instruction isolation |
| Validation | Pydantic | JSON schema enforcement |
| CI/CD | Docker + Jenkins | Automated test → build → deploy |
| Deployment | Streamlit Cloud | Production serving |
| Testing | pytest | Compliance + unit tests |

---

## 📝 Course Fingerprint

This project implements all **5 Stages** from the course scaffold:

- **Stage 1** — Secure Environment & Scaffold (ID Badge Protocol, dotenv)
- **Stage 2** — Relational Foundation (SQLite memory.db, table schema)
- **Stage 3** — Safety-First Custom Tooling (BaseTool, SafeQueryTool)
- **Stage 4** — Deep Role Engineering (Role/Goal/Backstory, schema in backstory)
- **Stage 5** — Task Orchestration & Memory Activation (Process.hierarchical, memory=True)

---

*Blueprint Blue · Week 18 · AI Agentic Systems Bootcamp*
