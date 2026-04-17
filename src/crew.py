"""
crew.py — Core orchestration script.
Follows the Week 18 Blueprint Blue architecture and course code fingerprint.
"""

## ---- Stage 1: Secure Environment & Scaffold (Weeks 1-3) ----
import os
import sqlite3
import requests
import yaml
from pathlib import Path
from dotenv import load_dotenv  # For Local Dev (Colab uses userdata)

load_dotenv()

## ---- Stage 2: The Relational Foundation (Week 14) ----
from crewai import Agent, Task, Crew, Process

## ---- Stage 3: Safety-First Custom Tooling (Weeks 7 & 14) ----
from crewai.tools import BaseTool
from crewai_tools import FileReadTool, SerperDevTool, FileWriteTool

## ---- Stage 4: Deep Role Engineering (Weeks 4, 11 & 14) ----
from src.tools.custom_tools import SafeQueryTool
from src.tools.database import setup_knowledge_db

# ── Config paths ──────────────────────────────────────────────────────────────
CONFIG_DIR = Path(__file__).parent.parent / "config"


def _load_config(filename: str) -> dict:
    with open(CONFIG_DIR / filename, "r") as f:
        return yaml.safe_load(f)


## ---- Stage 5: Task Orchestration & Memory Activation (Weeks 5, 9 & 14) ----

def build_crew(user_topic: str) -> Crew:
    """
    Assembles the full multi-agent crew following the R-A-R Pipeline pattern.
    Loads agent personas and task instructions from config/ YAML files.
    """
    agents_cfg = _load_config("agents.yaml")
    tasks_cfg  = _load_config("tasks.yaml")

    # ── Tools ─────────────────────────────────────────────────────────────────
    search_tool    = SerperDevTool()
    file_read_tool = FileReadTool(file_path="context_notes.txt")   # Semantic Vault
    file_write_tool = FileWriteTool()
    sql_tool       = SafeQueryTool()

    # ── Agents: personas loaded from config/agents.yaml ───────────────────────
    researcher = Agent(
        role=agents_cfg["researcher"]["role"],
        goal=agents_cfg["researcher"]["goal"],
        backstory=(
            agents_cfg["researcher"]["backstory"]
        ),
        tools=[search_tool, file_read_tool],
        verbose=True,
        allow_delegation=False,
    )

    analyst = Agent(
        role=agents_cfg["analyst"]["role"],
        goal=agents_cfg["analyst"]["goal"],
        backstory=(
            agents_cfg["analyst"]["backstory"]
        ),
        tools=[sql_tool, file_read_tool],
        verbose=True,
        allow_delegation=False,
    )

    writer = Agent(
        role=agents_cfg["writer"]["role"],
        goal=agents_cfg["writer"]["goal"],
        backstory=(
            agents_cfg["writer"]["backstory"]
        ),
        tools=[file_write_tool],
        verbose=True,
        allow_delegation=False,
    )

    # ── Tasks: instructions loaded from config/tasks.yaml ─────────────────────
    research_task = Task(
        description=tasks_cfg["research_task"]["description"].format(
            user_topic=user_topic
        ),
        expected_output=tasks_cfg["research_task"]["expected_output"],
        agent=researcher,
    )

    analysis_task = Task(
        description=tasks_cfg["analysis_task"]["description"].format(
            user_topic=user_topic
        ),
        expected_output=tasks_cfg["analysis_task"]["expected_output"],
        agent=analyst,
        context=[research_task],
    )

    writing_task = Task(
        description=tasks_cfg["writing_task"]["description"].format(
            user_topic=user_topic
        ),
        expected_output=tasks_cfg["writing_task"]["expected_output"],
        agent=writer,
        context=[research_task, analysis_task],
    )

    # ── Crew: Hierarchical process with memory (Week 14/19 standard) ──────────
    knowledge_assistant = Crew(
        agents=[researcher, analyst, writer],
        tasks=[research_task, analysis_task, writing_task],
        process=Process.hierarchical,        # True branching and selection
        manager_llm="gpt-4o",               # The implicit "Boss"
        memory=True,                         # Activating Semantic Memory Layer
        embedder={
            "provider": "openai",
            "config": {"model": "text-embedding-3-small"},
        },
        verbose=True,
    )

    return knowledge_assistant


def run_crew(user_topic: str) -> str:
    """
    Entry point. Initialises the database, builds and kicks off the crew.
    Wrapped in the Immune System (try/except) for graceful degradation.
    """
    try:
        setup_knowledge_db()                     # Ensure DB is ready
        crew   = build_crew(user_topic)
        result = crew.kickoff(inputs={"user_topic": user_topic})
        return str(result)
    except Exception as e:
        return f"Mission Failed: {e}"
    finally:
        print("── Mission complete. Cleanup initiated. ──")


if __name__ == "__main__":
    output = run_crew("AI Agentic Systems trends in 2025")
    print(output)
