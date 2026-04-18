"""
crew.py — Core Orchestration Script.

Implements the full R-A-R Pipeline (Research → Analysis → Reporting)
following the Week 18 Blueprint Blue architecture and course code fingerprint.

Architecture patterns applied:
  - Week 10-12 : verbose=True for Glass Box agent observation
  - Week 13    : Process.hierarchical — Manager Agent as oversight layer
  - Week 14    : SQLite memory.db + YAML config isolation + Execution Traces
  - Week 15    : Resilience Stack (retry, budget cap, JSON schema, reviewer)
  - Week 17    : FastAPI + Streamlit interface layer
  - Week 18    : Modular Blueprint Blue folder structure
"""

## ---- Stage 1: Secure Environment & Scaffold (Weeks 1-3) ----
# ID Badge Protocol: API keys loaded from .env — NEVER hardcoded in source.
# Use dotenv for local dev; google.colab.userdata for Colab environments.
import os
import yaml
import logging
from pathlib import Path
from dotenv import load_dotenv   # Local dev — Colab uses: from google.colab import userdata

load_dotenv()  # Loads .env → os.environ

# ── Logging: Glass Box Experience (Week 10) ───────────────────────────────────
# Makes every agent decision, tool call, and error visible and traceable.
# This is how we debug 'Agent Chaos' vs 'Coordinated Intelligence'.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

## ---- Stage 2: The Relational Foundation (Week 14) ----
# SQLite memory.db = the agent's persistent 'Hard Drive'.
# Separates Relational Memory (facts/SQL) from Semantic Memory (embeddings).
from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel

## ---- Stage 3: Safety-First Custom Tooling (Weeks 7 & 14) ----
# All tools inherit BaseTool — strict type-checking, no raw functions.
# SafeQueryTool enforces READ-ONLY access (Layer 2 Guardrail).
from crewai.tools import BaseTool
from crewai_tools import FileReadTool, SerperDevTool

from src.tools.custom_tools import SafeQueryTool, WebScraperTool, ContextWriterTool
from src.tools.database     import setup_knowledge_db, save_run
from src.tools.resilience   import (
    execute_with_retry,    # Layer 1: Exponential backoff + jitter
    apply_budget_cap,      # Layer 2: Token cap — Denial of Wallet prevention
    StructuredReport,      # Layer 3: JSON schema for output enforcement
    create_reviewer_agent, # Layer 4: Metacognition via Reviewer Agent
)
from src.tools.debug_tools  import ExecutionTracer, run_smoke_test

# ── Config paths (Week 18 pattern) ────────────────────────────────────────────
# Isolates 'instructions' from 'engine' — update personas in YAML, not code.
CONFIG_DIR = Path(__file__).parent.parent / "config"

# Global tracer — records timing, tool usage, and decision flow (Week 14)
tracer = ExecutionTracer()


def _load_config(filename: str) -> dict:
    """Loads a YAML config file from config/. Raises clear error if missing."""
    config_path = CONFIG_DIR / filename
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            "Check that config/{filename} exists (Week 18 structure)."
        )
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


## ---- Stage 4: Deep Role Engineering (Weeks 4, 11 & 14) ----
# Every agent is defined by: Role (what), Goal (why), Backstory (how).
# Analyst backstory hardcodes the DB schema so it never hallucinates column names.

def build_crew(user_topic: str) -> Crew:
    """
    Assembles the three-agent R-A-R crew with the full Resilience Stack.

    Phase 1 — Research  : Broad data ingestion via web search + Semantic Vault
    Phase 2 — Analysis  : SQL-grounded fact extraction + pattern identification
    Phase 3 — Reporting : Human-readable artifact generation (400-600 words)

    Args:
        user_topic: The topic/query to research, analyse, and report on.

    Returns:
        A configured Crew instance ready to .kickoff()
    """
    # ── Load YAML configs (separation of concerns — Week 18) ─────────────────
    agents_cfg = _load_config("agents.yaml")
    tasks_cfg  = _load_config("tasks.yaml")

    # ── Tools: each agent gets only the tools it needs (least privilege) ──────
    search_tool      = SerperDevTool()                              # Web search (Week 11)
    file_read_tool   = FileReadTool(file_path="context_notes.txt") # Semantic Vault (Week 14)
    sql_tool         = SafeQueryTool()                             # Read-only DB access (Week 14)
    scraper_tool     = WebScraperTool()                            # Direct URL fetcher (Week 7)
    ctx_writer_tool  = ContextWriterTool()                         # Qualitative memory writer

    # ── Phase 1: Researcher — broad data ingestion ────────────────────────────
    researcher = Agent(
        role     = agents_cfg["researcher"]["role"],
        goal     = agents_cfg["researcher"]["goal"],
        backstory= agents_cfg["researcher"]["backstory"],
        tools    = [search_tool, scraper_tool, file_read_tool],
        verbose  = True,           # Glass Box: shows thought + tool selection (Week 10)
        allow_delegation = False,  # Specialist worker — no sub-delegation
    )

    # ── Phase 2: Analyst — SQL-grounded fact extraction ──────────────────────
    # DB schema in backstory prevents hallucinated column/table names (Week 14)
    analyst = Agent(
        role     = agents_cfg["analyst"]["role"],
        goal     = agents_cfg["analyst"]["goal"],
        backstory= agents_cfg["analyst"]["backstory"],
        tools    = [sql_tool, file_read_tool],
        verbose  = True,           # Glass Box: makes SQL queries visible
        allow_delegation = False,
    )

    # ── Phase 3: Writer — human-readable artifact generation ─────────────────
    writer = Agent(
        role     = agents_cfg["writer"]["role"],
        goal     = agents_cfg["writer"]["goal"],
        backstory= agents_cfg["writer"]["backstory"],
        tools    = [ctx_writer_tool],
        verbose  = True,
        allow_delegation = False,
    )

    # Layer 2: Apply Budgetary Caps to prevent Denial of Wallet attacks
    for agent in [researcher, analyst, writer]:
        apply_budget_cap(agent, max_tokens=5000)

    # ── Tasks: instructions from config/tasks.yaml (Week 18) ─────────────────
    # {user_topic} placeholder is resolved at runtime — config stays generic.

    # Phase 1: Research Task — broad ingestion
    research_task = Task(
        description    = tasks_cfg["research_task"]["description"].format(user_topic=user_topic),
        expected_output= tasks_cfg["research_task"]["expected_output"],
        agent          = researcher,
    )

    # Phase 2: Analysis Task — distillation (context chains from Phase 1)
    analysis_task = Task(
        description    = tasks_cfg["analysis_task"]["description"].format(user_topic=user_topic),
        expected_output= tasks_cfg["analysis_task"]["expected_output"],
        agent          = analyst,
        context        = [research_task],  # Injects Phase 1 output as context (Week 9)
        output_json    = StructuredReport, # Layer 3: JSON schema enforcement (Week 15)
    )

    # Phase 3: Writing Task — human-readable artifact (context chains Phase 1+2)
    writing_task = Task(
        description    = tasks_cfg["writing_task"]["description"].format(user_topic=user_topic),
        expected_output= tasks_cfg["writing_task"]["expected_output"],
        agent          = writer,
        context        = [research_task, analysis_task],  # Full R-A-R context chain
    )

## ---- Stage 5: Task Orchestration & Memory Activation (Weeks 5, 9 & 14) ----

    # ── Crew: Hierarchical process with Semantic Memory ───────────────────────
    # Process.hierarchical: Manager Agent oversees workers, plans, reviews (Week 13)
    # memory=True: activates CrewAI's Semantic Memory (embeddings) layer (Week 14)
    # embedder: uses OpenAI text-embedding-3-small for cosine similarity search
    knowledge_assistant = Crew(
        agents     = [researcher, analyst, writer],
        tasks      = [research_task, analysis_task, writing_task],
        process    = Process.sequential,     # Sequential: R → A → W (stable in current CrewAI)
        memory     = True,                  # Semantic Memory Layer (Week 14)
        embedder   = {
            "provider": "openai",
            "config"  : {"model": "text-embedding-3-small"},
            # Cosine similarity threshold >0.75 for relevant context retrieval
        },
        verbose    = True,                  # Full execution trace to console
    )

    return knowledge_assistant


def run_crew(user_topic: str) -> str:
    """
    Entry point for the R-A-R Pipeline.

    Initialises the DB, starts the execution tracer, builds and kicks off
    the crew, persists the result, and handles errors gracefully.

    Immune System pattern (try/except/finally) ensures:
    - try   : attempt the primary mission
    - except: graceful degradation — log and return error string
    - finally: mandatory cleanup — always runs regardless of outcome
    """
    tracer.start_mission(user_topic)

    try:
        # Ensure memory.db is initialised before any agent runs (Week 14)
        setup_knowledge_db()
        logger.info(f"Starting R-A-R Pipeline for topic: '{user_topic}'")

        # Layer 1: Wrap crew kickoff in retry logic for API resilience (Week 15)
        crew   = build_crew(user_topic)
        result = execute_with_retry(
            lambda: str(crew.kickoff(inputs={"user_topic": user_topic})),
            max_retries=3,
        )

        # Persist result to run_history table (audit trail — Week 14)
        save_run(user_topic=user_topic, result=result, status="success")
        tracer.log_agent_action("Crew", "kickoff complete", tool_used="R-A-R Pipeline")
        tracer.end_mission(status="success")

        return result

    except Exception as e:
        # Graceful degradation — log error, persist failure, return message
        logger.error(f"Mission Failed: {e}")
        save_run(user_topic=user_topic, result=str(e), status="failed")
        tracer.end_mission(status="failed")
        return f"Mission Failed: {e}"

    finally:
        # Mandatory cleanup — always runs, even if exception occurred (Week 15)
        logger.info("── Mission complete. Cleanup initiated. ──")


if __name__ == "__main__":
    # Run smoke test first to verify environment (Week 16)
    run_smoke_test()
    output = run_crew("AI Agentic Systems trends in 2025")
    print(output)
