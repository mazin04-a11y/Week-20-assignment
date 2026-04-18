# AIOps Mission Dashboard — Full Setup Guide
### Windows 11 · Python 3.12 · CrewAI · Docker · Jenkins · Streamlit Cloud

---

## Overview

This guide sets up the complete AIOps Mission Dashboard from scratch on a fresh Windows 11 machine.
By the end you will have:
- A local Streamlit UI running CrewAI agents
- A FastAPI backend
- Jenkins CI/CD running inside Docker
- The app deployed publicly on Streamlit Cloud

**Time required:** ~45-60 minutes (most of it is waiting for downloads)

---

## PART 1 — Install System Dependencies

### Step 1: Install Python 3.12

Open **Command Prompt** (search "cmd" in Start) and run:

```
winget install Python.Python.3.12
```

Close and reopen the terminal when done. Verify:

```
python --version
```

Expected output: `Python 3.12.x`

> ⚠️ If `python` is not recognised, you may need to add it to PATH manually:
> Control Panel → System → Advanced System Settings → Environment Variables →
> add `C:\Users\<YourName>\AppData\Local\Programs\Python\Python312\` to Path.

---

### Step 2: Install Docker Desktop

```
winget install Docker.DockerDesktop
```

This requires a **restart** of your computer. After restart:
1. Open **Docker Desktop** from the Start menu
2. Wait for it to finish starting (the whale icon in the taskbar stops animating)
3. Verify in a new terminal:

```
docker --version
docker compose version
```

Expected output:
```
Docker version 27.x.x
Docker Compose version v2.x.x
```

> Docker Desktop must be **open and running** every time you use Jenkins.

---

### Step 3: Install Git

```
winget install Git.Git
```

Close and reopen the terminal. Verify:

```
git --version
```

Configure your identity (required for commits):

```
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

---

### Step 4: Install GitHub CLI

```
winget install GitHub.cli
```

Authenticate with GitHub:

```
gh auth login
```

When prompted:
- Select **GitHub.com**
- Select **HTTPS**
- Select **Login with a web browser**
- Copy the code shown, press Enter — your browser opens
- Paste the code and authorise

Verify:

```
gh auth status
```

---

### Step 5: Install VS Code (Recommended)

```
winget install Microsoft.VisualStudioCode
```

Install the Python extension inside VS Code after opening it.

---

## PART 2 — Create the Project

### Step 6: Create the Project Folder

Navigate to where you want the project. For this guide we use OneDrive Documents:

```
mkdir "C:\Users\%USERNAME%\OneDrive\Documents\Agentic AI BootCamp\Docker and Jenkins"
cd "C:\Users\%USERNAME%\OneDrive\Documents\Agentic AI BootCamp\Docker and Jenkins"
```

---

### Step 7: Create the Full Folder Structure

Run these commands one by one:

```
mkdir src
mkdir src\agents
mkdir src\tasks
mkdir src\tools
mkdir config
mkdir app
mkdir tests
mkdir jenkins
```

Create empty `__init__.py` files so Python treats folders as packages:

```
type nul > src\__init__.py
type nul > src\agents\__init__.py
type nul > src\tasks\__init__.py
type nul > src\tools\__init__.py
```

Your structure should now look like this:

```
Docker and Jenkins/
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   └── __init__.py
│   ├── tasks/
│   │   └── __init__.py
│   └── tools/
│       └── __init__.py
├── config/
├── app/
├── tests/
└── jenkins/
```

---

## PART 3 — Create All Project Files

Open VS Code in the project folder:

```
code .
```

Create each file below exactly as shown.

---

### File: `requirements.txt`

```
crewai>=0.80.0
crewai-tools>=0.15.0
fastapi>=0.115.0
uvicorn>=0.32.0
streamlit>=1.40.0
python-dotenv>=1.0.0
langchain-anthropic>=0.3.0
anthropic>=0.40.0
requests>=2.32.0
pydantic>=2.10.0
pyyaml>=6.0.0
pytest>=8.0.0
```

---

### File: `.env.example`

```
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
SERPER_API_KEY=your_serper_key_here
```

---

### File: `.env`

```
ANTHROPIC_API_KEY=
OPENAI_API_KEY=your_actual_openai_key
SERPER_API_KEY=your_actual_serper_key
```

> ⚠️ Replace the placeholder values with your real API keys.
> Get OpenAI keys at: platform.openai.com
> Get Serper keys at: serper.dev

---

### File: `.gitignore`

```
.env
__pycache__/
*.pyc
*.pyo
.pytest_cache/
*.egg-info/
dist/
build/
.venv/
venv/
*.log
context_notes.txt
memory.db
*.db
```

---

### File: `config/agents.yaml`

```yaml
researcher:
  role: "Senior Research Analyst"
  goal: >
    Uncover accurate, up-to-date intelligence on the given topic.
    Gather key facts, recent developments, and credible sources.
  backstory: >
    You are an expert research analyst at a top AI think tank.
    You specialise in finding accurate, real-world data using web search
    and structured sources. You never fabricate facts — if you cannot
    verify something, you say so.

analyst:
  role: "Data Analyst"
  goal: >
    Analyse the research findings and retrieve grounded numerical facts
    from the database. Produce a structured analysis without hallucination.
  backstory: >
    You are a precision-focused data analyst who only provides facts
    grounded in structured SQL data. You have direct access to the
    knowledge database (memory.db) which contains tables:
    research_findings (topic, finding, source),
    run_history (user_topic, result, status), and
    knowledge_items (category, item, value, metadata).
    You always use SUM() instead of COUNT(*) when calculating totals.
    You never invent numbers or statuses.

writer:
  role: "Content Writer"
  goal: >
    Transform research and analysis into a polished, professional report
    ready for deployment. Structure: Introduction → Key Findings → Conclusion.
  backstory: >
    You are a skilled technical writer who turns raw research and data
    analysis into clear, compelling professional reports. You prioritise
    accuracy over creativity — every claim must be traceable to the
    research or analysis provided in context.
```

---

### File: `config/tasks.yaml`

```yaml
research_task:
  description: >
    Research the following topic thoroughly: '{user_topic}'.
    Use web search to find recent, accurate information.
    Identify at least 3 key findings with their sources.
    Save important context to the Semantic Vault using the Context Writer Tool.
  expected_output: >
    A structured research summary containing:
    1. At least 3 key findings with sources
    2. Recent developments (last 12 months)
    3. Any relevant data points or statistics

analysis_task:
  description: >
    Analyse the research findings on '{user_topic}'.
    Query the knowledge database for any related stored facts.
    Cross-reference web findings with database records.
    Identify patterns, gaps, and key insights.
    Use SUM() for any numerical aggregations — never estimate.
  expected_output: >
    A structured analysis report containing:
    1. Key patterns and insights from the research
    2. Any grounded facts retrieved from the database
    3. Identified gaps or areas requiring caution
    4. Confidence level for each major claim (High/Medium/Low)

writing_task:
  description: >
    Write a professional report on '{user_topic}' using the research
    and analysis provided in context.
    Structure: Introduction → Key Findings → Analysis → Conclusion.
    Every claim must be traceable to the context provided.
    Target length: 400-600 words. Professional tone.
  expected_output: >
    A complete, publication-ready report (400-600 words) with:
    1. Introduction (what and why)
    2. Key Findings (at least 3, with supporting detail)
    3. Analysis (patterns, implications)
    4. Conclusion (summary and next steps)
```

---

### File: `src/tools/database.py`

```python
"""
database.py — SQLite Hard Drive (Week 14).
Sets up memory.db and provides save/query helpers.
"""
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

DEFAULT_DB = "memory.db"


def setup_knowledge_db(db_path: str = DEFAULT_DB):
    """Creates all required tables in memory.db if they don't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_findings (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            topic      TEXT,
            finding    TEXT,
            source     TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS run_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_topic  TEXT,
            result      TEXT,
            status      TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_items (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            key        TEXT,
            value      TEXT,
            category   TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()
    logger.info("memory.db initialised with all tables.")


def save_run(user_topic: str, result: str, status: str, db_path: str = DEFAULT_DB):
    """Saves a crew run result to the run_history table."""
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO run_history (user_topic, result, status) VALUES (?, ?, ?)",
            (user_topic, result, status)
        )
        conn.commit()
        conn.close()
        logger.info(f"Run saved to DB — topic: '{user_topic}', status: {status}")
    except Exception as e:
        logger.error(f"Failed to save run to DB: {e}")
```

---

### File: `src/tools/custom_tools.py`

```python
"""
custom_tools.py — Custom BaseTool implementations (Week 7 + 14).
SafeQueryTool: read-only SQL guardrail.
WebScraperTool: direct URL content fetcher.
ContextWriterTool: writes to the Semantic Vault (context_notes.txt).
"""
import sqlite3
import requests
import logging
from crewai.tools import BaseTool

logger = logging.getLogger(__name__)


class SafeQueryTool(BaseTool):
    name: str = "database_query_tool"
    description: str = (
        "Read-only SQL query tool for memory.db. "
        "Use SELECT statements only. Never use DROP, DELETE, UPDATE, or INSERT."
    )

    def _run(self, query: str) -> str:
        # Layer 2 Guardrail: block all destructive SQL
        blocked = ['DROP', 'DELETE', 'UPDATE', 'INSERT']
        if any(k in query.upper() for k in blocked):
            raise ValueError("Action Prohibited: Read Only Access")
        try:
            conn = sqlite3.connect("memory.db")
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            return f"Retrieved data: {results}"
        except Exception as e:
            return f"Database Error: {e}"


class WebScraperTool(BaseTool):
    name: str = "web_scraper_tool"
    description: str = (
        "Fetches raw HTML content from a given URL. "
        "Use when you need to read the full content of a specific web page."
    )

    def _run(self, url: str) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text[:5000]  # Cap at 5000 chars
        except Exception as e:
            return f"Scrape Error: {e}"


class ContextWriterTool(BaseTool):
    name: str = "context_writer_tool"
    description: str = (
        "Writes qualitative research notes to context_notes.txt (Semantic Vault). "
        "Use to save important findings for later retrieval."
    )

    def _run(self, content: str) -> str:
        try:
            with open("context_notes.txt", "a", encoding="utf-8") as f:
                f.write(content + "\n\n")
            return "Context saved to Semantic Vault."
        except Exception as e:
            return f"Write Error: {e}"
```

---

### File: `src/tools/resilience.py`

```python
"""
resilience.py — 4-Layer Resilience Stack (Week 15).
Layer 1: Exponential backoff retry
Layer 2: Token budget cap
Layer 3: JSON schema enforcement (Pydantic)
Layer 4: Reviewer agent metacognition
"""
import time
import random
import json
import logging
from typing import Callable, Any, Optional, List
from pydantic import BaseModel, ValidationError
from crewai import Agent, Task

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mission_log.txt"),
    ]
)
logger = logging.getLogger(__name__)


# ── Layer 1: Retry ────────────────────────────────────────────────────────────

def execute_with_retry(api_call_func: Callable, max_retries: int = 3) -> Any:
    """Exponential backoff + jitter retry wrapper."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return api_call_func()
        except Exception as e:
            last_error = e
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                f"Retrying in {wait_time:.2f}s..."
            )
            time.sleep(wait_time)
    raise Exception(f"Layer 1 Failure: Max retries exceeded. Last error: {last_error}")


# ── Layer 2: Budget Cap ───────────────────────────────────────────────────────

MAX_TOKENS_PER_CALL = 5000

def apply_budget_cap(agent: Agent, max_tokens: int = MAX_TOKENS_PER_CALL) -> Agent:
    """Applies a token budget cap to an agent to prevent runaway costs."""
    if hasattr(agent, 'llm') and agent.llm:
        agent.llm.max_tokens = max_tokens
        logger.info(f"[Layer 2] Budget cap applied: {max_tokens} tokens on '{agent.role}'")
    return agent


def check_query_budget(query: str, max_length: int = 2000) -> bool:
    """Rejects inputs that exceed the character budget."""
    if len(query) > max_length:
        logger.warning(f"[Layer 2] Query rejected: {len(query)} chars exceeds {max_length}.")
        return False
    return True


# ── Layer 3: JSON Schema ──────────────────────────────────────────────────────

class StructuredReport(BaseModel):
    """JSON schema for structured analysis output (Layer 3)."""
    title:    str        # Report title
    summary:  str        # Executive summary
    findings: List[str]  # List of key findings
    sources:  List[str]  # List of source URLs or references
    status:   str        # "complete" | "partial" | "failed"


def validate_json_output(raw_output: str, schema: type = StructuredReport) -> Optional[dict]:
    """Validates and parses JSON output from agents against the Pydantic schema."""
    try:
        data = json.loads(raw_output)
        validated = schema(**data)
        logger.info("[Layer 3] JSON output validated successfully.")
        return validated.model_dump()
    except json.JSONDecodeError as e:
        logger.error(f"[Layer 3] JSON parse error: {e}")
        return None
    except ValidationError as e:
        logger.error(f"[Layer 3] Schema validation error: {e}")
        return None


# ── Layer 4: Reviewer Agent ───────────────────────────────────────────────────

def create_reviewer_agent() -> Agent:
    """Creates a metacognition reviewer agent that fact-checks draft outputs."""
    return Agent(
        role="Quality Reviewer",
        goal=(
            "Ensure semantic accuracy by critiquing the writer's output "
            "against the original research. Flag hallucinated citations or "
            "unsupported claims."
        ),
        backstory=(
            "You are a meticulous fact-checker. Your only job is to compare "
            "the draft report against original research sources and identify "
            "discrepancies. Output either APPROVED or a numbered list of corrections."
        ),
        verbose=True,
        allow_delegation=False,
    )
```

---

### File: `src/tools/debug_tools.py`

```python
"""
debug_tools.py — Debugging, Tracing & Diagnostics Toolkit (Weeks 14/16/18).
"""
import os
import sys
import time
import sqlite3
import logging
import platform
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

logger = logging.getLogger(__name__)


def run_smoke_test() -> dict:
    """Week 16: Environment Diagnostics Table — run before every deployment."""
    results = {}

    # Python version
    py_version = sys.version_info
    results["Python >= 3.12"] = (
        py_version >= (3, 12),
        f"Found Python {py_version.major}.{py_version.minor}.{py_version.micro}"
    )

    # API keys
    for key in ["OPENAI_API_KEY", "SERPER_API_KEY"]:
        val = os.environ.get(key, "")
        results[f"Env: {key}"] = (
            bool(val),
            "SET ✓" if val else "MISSING ✗ — add to .env file"
        )

    # Required files
    base = Path(__file__).parent.parent.parent
    required_files = [
        "src/crew.py",
        "src/tools/custom_tools.py",
        "src/tools/database.py",
        "src/tools/resilience.py",
        "config/agents.yaml",
        "config/tasks.yaml",
        "app/streamlit_app.py",
        "app/main.py",
        ".env",
        "requirements.txt",
    ]
    for f in required_files:
        exists = (base / f).exists()
        results[f"File: {f}"] = (exists, "Found ✓" if exists else "MISSING ✗")

    # Database
    try:
        conn = sqlite3.connect("memory.db")
        conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        conn.close()
        results["DB: memory.db"] = (True, "Accessible ✓")
    except Exception as e:
        results["DB: memory.db"] = (False, f"Error: {e}")

    # Core imports
    for pkg in ["crewai", "streamlit", "fastapi", "pydantic", "yaml", "dotenv"]:
        try:
            __import__(pkg)
            results[f"Import: {pkg}"] = (True, "OK ✓")
        except ImportError:
            results[f"Import: {pkg}"] = (False, f"NOT INSTALLED ✗ — run: pip install {pkg}")

    print("\n" + "=" * 60)
    print("  SMOKE TEST — Environment Diagnostics Table (Week 16)")
    print("=" * 60)
    passed_count = 0
    for check, (ok, detail) in results.items():
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {status}  {check:<35} {detail}")
        if ok:
            passed_count += 1
    print("=" * 60)
    print(f"  Result: {passed_count}/{len(results)} checks passed")
    print("=" * 60 + "\n")

    return results


class ExecutionTracer:
    """Week 14: Records timing, tool usage, and decision flow for every crew run."""

    def __init__(self):
        self.traces = []
        self.start_time: Optional[float] = None

    def start_mission(self, topic: str):
        self.start_time = time.time()
        self.traces = []
        logger.info(f"[TRACE] Mission started: '{topic}'")

    def log_agent_action(self, agent_role: str, action: str, tool_used: Optional[str] = None):
        entry = {
            "event": "AGENT_ACTION",
            "timestamp": datetime.now().isoformat(),
            "agent_role": agent_role,
            "action": action,
            "tool_used": tool_used or "none",
            "elapsed_s": round(time.time() - (self.start_time or time.time()), 2),
        }
        self.traces.append(entry)
        logger.info(f"[TRACE] {agent_role} → {action}" + (f" (tool: {tool_used})" if tool_used else ""))

    def end_mission(self, status: str = "success"):
        elapsed = round(time.time() - (self.start_time or time.time()), 2)
        logger.info(f"[TRACE] Mission ended — status: {status}, elapsed: {elapsed}s")
        print("\n" + "=" * 60)
        print("  EXECUTION TRACE (Week 14 — Decision Flow)")
        print("=" * 60)
        for t in self.traces:
            if t["event"] == "AGENT_ACTION":
                print(f"  [{t['elapsed_s']:>6}s] {t['agent_role']:<25} → {t['action']}")
                if t["tool_used"] != "none":
                    print(f"           {'':25}   🔧 Tool: {t['tool_used']}")
        print("-" * 60)
        print(f"  Total elapsed : {elapsed}s")
        print(f"  Final status  : {status.upper()}")
        print("=" * 60 + "\n")


def run_golive_checklist() -> bool:
    """Week 18: Final verification before deploying to Blueprint Blue."""
    base = Path(__file__).parent.parent.parent
    checks = []

    print("\n" + "=" * 60)
    print("  GO-LIVE CHECKLIST (Week 18 — Blueprint Blue)")
    print("=" * 60)

    def check(label: str, passed: bool, fix: str = ""):
        icon = "✅" if passed else "❌"
        print(f"  {icon}  {label}")
        if not passed and fix:
            print(f"      FIX: {fix}")
        checks.append(passed)

    check("src/ directory exists",      (base / "src").is_dir())
    check("config/ directory exists",   (base / "config").is_dir())
    check("tests/ directory exists",    (base / "tests").is_dir())
    check("config/agents.yaml present", (base / "config/agents.yaml").exists())
    check("config/tasks.yaml present",  (base / "config/tasks.yaml").exists())

    gitignore = (base / ".gitignore").read_text() if (base / ".gitignore").exists() else ""
    check(".env in .gitignore",     ".env"      in gitignore, "Add .env to .gitignore")
    check("memory.db in .gitignore","memory.db" in gitignore, "Add memory.db to .gitignore")
    check("requirements.txt present", (base / "requirements.txt").exists())
    check("README.md present",        (base / "README.md").exists())

    all_passed = all(checks)
    print("-" * 60)
    print(f"  Result: {'READY FOR DEPLOYMENT 🚀' if all_passed else 'NOT READY — fix issues above ⚠️'}")
    print("=" * 60 + "\n")
    return all_passed


if __name__ == "__main__":
    run_smoke_test()
    run_golive_checklist()
```

---

### File: `src/crew.py`

```python
"""
crew.py — Core Orchestration Script.
R-A-R Pipeline: Research → Analyse → Report
Week 18 Blueprint Blue architecture.
"""
import os
import yaml
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel
from crewai.tools import BaseTool
from crewai_tools import FileReadTool, SerperDevTool

from src.tools.custom_tools import SafeQueryTool, WebScraperTool, ContextWriterTool
from src.tools.database     import setup_knowledge_db, save_run
from src.tools.resilience   import (
    execute_with_retry,
    apply_budget_cap,
    StructuredReport,
    create_reviewer_agent,
)
from src.tools.debug_tools  import ExecutionTracer, run_smoke_test

CONFIG_DIR = Path(__file__).parent.parent / "config"
tracer = ExecutionTracer()


def _load_config(filename: str) -> dict:
    config_path = CONFIG_DIR / filename
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def build_crew(user_topic: str) -> Crew:
    agents_cfg = _load_config("agents.yaml")
    tasks_cfg  = _load_config("tasks.yaml")

    search_tool     = SerperDevTool()
    file_read_tool  = FileReadTool(file_path="context_notes.txt")
    sql_tool        = SafeQueryTool()
    scraper_tool    = WebScraperTool()
    ctx_writer_tool = ContextWriterTool()

    researcher = Agent(
        role     = agents_cfg["researcher"]["role"],
        goal     = agents_cfg["researcher"]["goal"],
        backstory= agents_cfg["researcher"]["backstory"],
        tools    = [search_tool, scraper_tool, file_read_tool],
        verbose  = True,
        allow_delegation = False,
    )

    analyst = Agent(
        role     = agents_cfg["analyst"]["role"],
        goal     = agents_cfg["analyst"]["goal"],
        backstory= agents_cfg["analyst"]["backstory"],
        tools    = [sql_tool, file_read_tool],
        verbose  = True,
        allow_delegation = False,
    )

    writer = Agent(
        role     = agents_cfg["writer"]["role"],
        goal     = agents_cfg["writer"]["goal"],
        backstory= agents_cfg["writer"]["backstory"],
        tools    = [ctx_writer_tool],
        verbose  = True,
        allow_delegation = False,
    )

    for agent in [researcher, analyst, writer]:
        apply_budget_cap(agent, max_tokens=5000)

    research_task = Task(
        description    = tasks_cfg["research_task"]["description"].format(user_topic=user_topic),
        expected_output= tasks_cfg["research_task"]["expected_output"],
        agent          = researcher,
    )

    analysis_task = Task(
        description    = tasks_cfg["analysis_task"]["description"].format(user_topic=user_topic),
        expected_output= tasks_cfg["analysis_task"]["expected_output"],
        agent          = analyst,
        context        = [research_task],
        output_json    = StructuredReport,
    )

    writing_task = Task(
        description    = tasks_cfg["writing_task"]["description"].format(user_topic=user_topic),
        expected_output= tasks_cfg["writing_task"]["expected_output"],
        agent          = writer,
        context        = [research_task, analysis_task],
    )

    crew = Crew(
        agents  = [researcher, analyst, writer],
        tasks   = [research_task, analysis_task, writing_task],
        process = Process.sequential,
        memory  = True,
        embedder= {
            "provider": "openai",
            "config"  : {"model": "text-embedding-3-small"},
        },
        verbose = True,
    )

    return crew


def run_crew(user_topic: str) -> str:
    tracer.start_mission(user_topic)
    try:
        setup_knowledge_db()
        logger.info(f"Starting R-A-R Pipeline for topic: '{user_topic}'")
        crew   = build_crew(user_topic)
        result = execute_with_retry(
            lambda: str(crew.kickoff(inputs={"user_topic": user_topic})),
            max_retries=3,
        )
        save_run(user_topic=user_topic, result=result, status="success")
        tracer.log_agent_action("Crew", "kickoff complete", tool_used="R-A-R Pipeline")
        tracer.end_mission(status="success")
        return result
    except Exception as e:
        logger.error(f"Mission Failed: {e}")
        save_run(user_topic=user_topic, result=str(e), status="failed")
        tracer.end_mission(status="failed")
        return f"Mission Failed: {e}"
    finally:
        logger.info("── Mission complete. Cleanup initiated. ──")


if __name__ == "__main__":
    run_smoke_test()
    output = run_crew("AI Agentic Systems trends in 2025")
    print(output)
```

---

### File: `app/streamlit_app.py`

```python
"""
streamlit_app.py — AIOps Mission Dashboard (Week 17).
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.crew             import run_crew
from src.tools.database   import setup_knowledge_db, save_run
from src.tools.debug_tools import run_smoke_test

st.set_page_config(
    page_title="AIOps Mission Dashboard",
    page_icon="🤖",
    layout="wide",
)

if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "run_count"   not in st.session_state:
    st.session_state["run_count"]   = 0
if "last_topic"  not in st.session_state:
    st.session_state["last_topic"]  = ""
if "debug_mode"  not in st.session_state:
    st.session_state["debug_mode"]  = False

with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("**Pipeline Stack**")
    st.markdown("- 🧠 CrewAI R-A-R Pipeline")
    st.markdown("- 🔍 SerperDevTool (web search)")
    st.markdown("- 🗄️ SQLite (memory.db — Hard Drive)")
    st.markdown("- 🔒 SafeQueryTool (read-only guardrail)")
    st.markdown("- 📄 FileReadTool (Semantic Vault)")
    st.divider()
    st.markdown("**Architecture (Week 13/14)**")
    st.markdown("- `Process.sequential`")
    st.markdown("- `memory=True` (Semantic Layer)")
    st.markdown("- 3-agent crew: Research → Analyse → Write")
    st.divider()
    st.markdown("**Resilience Stack (Week 15)**")
    st.markdown("- L1: Exponential backoff retry")
    st.markdown("- L2: max_tokens=5000 cap")
    st.markdown("- L3: JSON schema enforcement")
    st.markdown("- L4: Reviewer metacognition")
    st.divider()
    st.session_state["debug_mode"] = st.toggle(
        "🔬 Debug Mode",
        value=st.session_state["debug_mode"],
    )
    st.markdown(f"**Session runs:** {st.session_state['run_count']}")
    if st.session_state["last_topic"]:
        st.markdown(f"**Last topic:** {st.session_state['last_topic'][:40]}...")
    st.caption("Blueprint Blue · Streamlit Cloud")

st.title("🤖 AIOps Mission Dashboard")
st.caption("R-A-R Pipeline: Research → Analyse → Report  |  Week 18 Blueprint Blue")
st.divider()

with st.form("input_form"):
    user_topic = st.text_input(
        "🎯 Mission Topic",
        placeholder="e.g. AI Agentic Systems trends in 2025",
        value=st.session_state["last_topic"],
    )
    col1, col2 = st.columns([3, 1])
    with col1:
        submitted   = st.form_submit_button("🚀 Run Agents", use_container_width=True)
    with col2:
        smoke_check = st.form_submit_button("🔬 Smoke Test", use_container_width=True)

if smoke_check:
    with st.spinner("Running environment diagnostics..."):
        results = run_smoke_test()
    passed = sum(1 for ok, _ in results.values() if ok)
    total  = len(results)
    if passed == total:
        st.success(f"✅ All {total} checks passed — ready for deployment.")
    else:
        st.warning(f"⚠️ {passed}/{total} checks passed.")
    with st.expander("📋 Diagnostics Detail", expanded=True):
        for check, (ok, detail) in results.items():
            icon = "✅" if ok else "❌"
            st.markdown(f"{icon} **{check}** — {detail}")

if submitted:
    if not user_topic.strip():
        st.warning("⚠️ Please enter a mission topic before running.")
    else:
        st.session_state["last_topic"] = user_topic.strip()
        try:
            setup_knowledge_db()
            with st.spinner("🔍 Agents are researching... (this may take 1-3 minutes)"):
                result = run_crew(user_topic.strip())
            st.session_state["last_result"] = result
            st.session_state["run_count"]  += 1
            save_run(user_topic=user_topic.strip(), result=result, status="success")
            st.success("✅ Mission Complete!")
            st.divider()
            st.markdown("### 📋 Mission Report")
            st.markdown(result)
            st.download_button(
                label     = "📥 Download Report",
                data      = result,
                file_name = f"report_{user_topic[:30].replace(' ', '_')}.md",
                mime      = "text/markdown",
            )
        except Exception as e:
            save_run(user_topic=user_topic.strip(), result=str(e), status="failed")
            st.error(f"System Error: {e}")

if st.session_state["debug_mode"]:
    st.divider()
    st.markdown("### 🔬 Debug Panel")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Session State**")
        st.json({
            "run_count" : st.session_state["run_count"],
            "last_topic": st.session_state["last_topic"],
            "has_result": st.session_state["last_result"] is not None,
        })
    with col_b:
        st.markdown("**Environment**")
        import platform
        st.json({
            "python"        : platform.python_version(),
            "os"            : platform.system(),
            "openai_key_set": bool(os.environ.get("OPENAI_API_KEY")),
            "serper_key_set": bool(os.environ.get("SERPER_API_KEY")),
        })
    if st.session_state["last_result"]:
        with st.expander("📄 Last Raw Result"):
            st.text(st.session_state["last_result"])
```

---

### File: `app/main.py`

```python
"""
main.py — FastAPI Interface Layer (Week 17/18).
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from src.crew import run_crew
from src.tools.database import setup_knowledge_db, save_run

app = FastAPI(
    title="AIOps Mission API",
    description="Interface Layer for the R-A-R Pipeline CrewAI service.",
    version="1.0.0",
)

setup_knowledge_db()


@app.get("/")
def health_check():
    return {"status": "online", "service": "AIOps Mission API"}


@app.post("/kickoff")
def kickoff(data: dict):
    user_topic = data.get("user_topic", "").strip()
    if not user_topic:
        return {"status": "error", "result": "user_topic is required"}
    try:
        result = run_crew(user_topic)
        save_run(user_topic=user_topic, result=result, status="success")
        return {"status": "success", "result": result}
    except Exception as e:
        save_run(user_topic=user_topic, result=str(e), status="failed")
        return {"status": "error", "result": f"Mission Failed: {e}"}
```

---

### File: `Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

### File: `docker-compose.yml`

```yaml
version: "3.8"

services:

  jenkins:
    image: jenkins/jenkins:lts
    container_name: jenkins
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped

  app:
    build: .
    container_name: aiops-app
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - .:/app
    restart: unless-stopped

volumes:
  jenkins_home:
```

---

### File: `Jenkinsfile`

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                sh 'pytest tests/ -v'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t aiops-mission-dashboard .'
            }
        }

        stage('Push to GitHub') {
            steps {
                sh 'git push origin master'
            }
        }
    }

    post {
        success {
            echo 'Pipeline complete — Streamlit Cloud will redeploy automatically.'
        }
        failure {
            echo 'Pipeline failed — check the logs above.'
        }
    }
}
```

---

### File: `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "aiops-mission-dashboard"
version = "1.0.0"
requires-python = ">=3.12"
dependencies = []
```

---

## PART 4 — Virtual Environment & Install

### Step 8: Create Virtual Environment

In your project folder terminal:

```
python -m venv venv
```

Activate it:

```
venv\Scripts\activate
```

Your terminal prompt will change to show `(venv)`.

> ⚠️ **Every time you open a new terminal** to work on this project, you must activate the venv first:
> `venv\Scripts\activate`

---

### Step 9: Install Dependencies

```
pip install -r requirements.txt
```

This takes 3-5 minutes. Wait for it to complete fully.

---

### Step 10: Run Smoke Test

```
python src/tools/debug_tools.py
```

You should see **20/20 checks passed**. If anything fails:
- ❌ Env keys → check your `.env` file has real values
- ❌ File missing → check you created all files in Part 3
- ❌ Import failed → re-run `pip install -r requirements.txt`

---

## PART 5 — Run Locally

### Step 11: Run the Streamlit Dashboard

```
streamlit run app/streamlit_app.py
```

Opens at: **http://localhost:8501**

Type a topic, click **🚀 Run Agents**. The pipeline takes 1-3 minutes.

### Step 12: Run the FastAPI Backend (Optional)

In a second terminal (with venv activated):

```
uvicorn app.main:app --reload
```

API docs at: **http://localhost:8000/docs**

Test it with a POST request:
```json
POST http://localhost:8000/kickoff
{"user_topic": "AI trends 2026"}
```

---

## PART 6 — GitHub

### Step 13: Create GitHub Repository

Go to **github.com** → click **New Repository**:
- Name: `agentic-ai-bootcamp`
- Visibility: **Private** (your API structure is in here)
- Do NOT initialise with README (we already have one)
- Click **Create repository**

### Step 14: Push to GitHub

In your project terminal:

```
git init
git add .
git commit -m "Initial Blueprint Blue setup"
git branch -M master
git remote add origin https://github.com/YOUR-USERNAME/agentic-ai-bootcamp.git
git push -u origin master
```

> Replace `YOUR-USERNAME` with your GitHub username.

Verify `.env` was NOT pushed:
```
git status
```
The `.env` file should not appear — it is gitignored.

---

## PART 7 — Docker + Jenkins

### Step 15: Start Docker Desktop

Open **Docker Desktop** from the Start menu. Wait until the whale icon in the taskbar is stable (not animating). This must be running before Jenkins can start.

### Step 16: Start Jenkins

In your project folder terminal:

```
docker compose up -d
```

This pulls the Jenkins image and starts it in the background. First run takes ~2 minutes.

Verify it's running:

```
docker ps
```

You should see `jenkins` and `aiops-app` in the list with status `Up`.

### Step 17: Access Jenkins

Open: **http://localhost:8080**

Jenkins starts with no authentication on first run — you access it directly, no password needed.

### Step 18: Configure Jenkins Pipeline

1. Click **New Item**
2. Enter name: `AIOps-Pipeline`
3. Select **Pipeline** → click OK
4. Scroll to **Pipeline** section
5. Set Definition to: **Pipeline script from SCM**
6. SCM: **Git**
7. Repository URL: `https://github.com/YOUR-USERNAME/agentic-ai-bootcamp.git`
8. Branch: `*/master`
9. Script Path: `Jenkinsfile`
10. Click **Save**

To run the pipeline: click **Build Now**.

### Step 19: Stop Jenkins (when done)

```
docker compose down
```

---

## PART 8 — Streamlit Cloud Deployment

### Step 20: Deploy to Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with your **GitHub account**
3. Click **"Create app"**
4. Fill in:
   - **Repository:** `YOUR-USERNAME/agentic-ai-bootcamp`
   - **Branch:** `master`
   - **Main file path:** `app/streamlit_app.py`
5. Click **"Advanced settings"**
6. Add your secrets (same as `.env`):
   ```
   OPENAI_API_KEY = "sk-proj-..."
   SERPER_API_KEY = "..."
   ```
7. Click **Deploy**

Streamlit Cloud builds and deploys automatically. Takes ~3 minutes first time.

Your app will be live at:
```
https://YOUR-USERNAME-agentic-ai-bootcamp-app-streamlit-app-XXXXX.streamlit.app
```

### Step 21: Auto-Deploy on Every Push

From this point forward:
- Every `git push origin master` triggers Streamlit Cloud to **automatically redeploy**
- No manual steps needed
- Jenkins pipeline handles the push after tests pass

---

## PART 9 — Daily Workflow

Every time you work on this project:

```bash
# 1. Open terminal in project folder
cd "C:\Users\%USERNAME%\OneDrive\Documents\Agentic AI BootCamp\Docker and Jenkins"

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Start Docker Desktop (if using Jenkins)
# Open Docker Desktop from Start menu

# 4. Run the app
streamlit run app/streamlit_app.py

# 5. When done — push changes to GitHub
git add .
git commit -m "Your message here"
git push origin master
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` not recognised | Add Python to PATH in Environment Variables |
| `venv\Scripts\activate` fails | Run in CMD, not PowerShell. Or use: `Set-ExecutionPolicy RemoteSigned` in PowerShell |
| Smoke test shows MISSING API keys | Check `.env` file has real values, no spaces around `=` |
| `Import: crewai` fails | Re-run `pip install -r requirements.txt` with venv activated |
| Docker not starting | Open Docker Desktop first and wait for it to fully load |
| Jenkins at localhost:8080 not loading | Run `docker compose up -d` and wait 2 minutes |
| Streamlit shows `Mission Failed` | Check OpenAI API key has credits. Check Serper key is valid |
| `FileNotFoundError: context_notes.txt` | Normal on first run — the file gets created automatically |

---

## File Checklist

Before running the smoke test, confirm every file exists:

```
✅ src/__init__.py
✅ src/crew.py
✅ src/agents/__init__.py
✅ src/tasks/__init__.py
✅ src/tools/__init__.py
✅ src/tools/custom_tools.py
✅ src/tools/database.py
✅ src/tools/resilience.py
✅ src/tools/debug_tools.py
✅ config/agents.yaml
✅ config/tasks.yaml
✅ app/streamlit_app.py
✅ app/main.py
✅ tests/
✅ .env (with real API keys)
✅ .env.example
✅ .gitignore
✅ requirements.txt
✅ pyproject.toml
✅ Dockerfile
✅ docker-compose.yml
✅ Jenkinsfile
```

---

*AIOps Mission Dashboard · Blueprint Blue · Week 18 · AI Agentic Systems Bootcamp*
