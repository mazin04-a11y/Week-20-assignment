"""
research_agents.py — Modular agent definitions.
Deep Role Engineering pattern (Weeks 4, 11 & 14).
Each agent has a distinct Role, Goal, and Backstory.
"""

## ---- Stage 4: Deep Role Engineering (Weeks 4, 11 & 14) ----
from crewai import Agent
from crewai_tools import SerperDevTool, FileReadTool
from src.tools.custom_tools import SafeQueryTool, WebScraperTool, ContextWriterTool


def create_researcher() -> Agent:
    """
    Phase 1 agent: broad data ingestion.
    Uses web search + semantic vault read to gather raw intelligence.
    """
    return Agent(
        role="Senior Research Analyst",
        goal=(
            "Uncover accurate, up-to-date intelligence on the given topic. "
            "Gather key facts, recent developments, and credible sources."
        ),
        backstory=(
            "You are an expert research analyst at a top AI think tank. "
            "You specialise in finding accurate, real-world data using web "
            "search and structured sources. You never fabricate facts — "
            "if you cannot verify something, you say so."
        ),
        tools=[SerperDevTool(), WebScraperTool(), FileReadTool(file_path="context_notes.txt")],
        verbose=True,
        allow_delegation=False,
    )


def create_analyst() -> Agent:
    """
    Phase 2 agent: distillation and analysis.
    Queries the SQL database for grounded facts — never hallucinates numbers.
    Schema awareness is hardcoded in backstory (Week 14 pattern).
    """
    return Agent(
        role="Data Analyst",
        goal=(
            "Analyse the research findings and retrieve grounded numerical facts "
            "from the database. Produce a structured analysis without hallucination."
        ),
        backstory=(
            "You are a precision-focused data analyst who only provides facts "
            "grounded in structured SQL data. You have direct access to the "
            "knowledge database (memory.db) which contains tables: "
            "research_findings (topic, finding, source), "
            "run_history (user_topic, result, status), and "
            "knowledge_items (category, item, value, metadata). "
            "You always use SUM() instead of COUNT(*) when calculating totals. "
            "You never invent numbers or statuses."
        ),
        tools=[SafeQueryTool(), FileReadTool(file_path="context_notes.txt")],
        verbose=True,
        allow_delegation=False,
    )


def create_writer() -> Agent:
    """
    Phase 3 agent: human-readable artifact generation.
    Maps data fields to report template sections.
    """
    return Agent(
        role="Content Writer",
        goal=(
            "Transform research and analysis into a polished, professional report "
            "ready for deployment. Structure: Introduction → Key Findings → Conclusion."
        ),
        backstory=(
            "You are a skilled technical writer who turns raw research and data "
            "analysis into clear, compelling professional reports. You prioritise "
            "accuracy over creativity — every claim must be traceable to the "
            "research or analysis provided in context."
        ),
        tools=[ContextWriterTool()],
        verbose=True,
        allow_delegation=False,
    )
