"""
research_tasks.py — Task definitions for the R-A-R Pipeline.
Follows the Week 14 Task constructor pattern.
Each task has a precise description with {user_topic} placeholder
and a machine-readable expected_output.
"""

## ---- Stage 5: Task Orchestration & Memory Activation (Weeks 5, 9 & 14) ----
from crewai import Task
from crewai import Agent


def create_research_task(agent: Agent, user_topic: str) -> Task:
    """Phase 1 — Research: broad data ingestion."""
    return Task(
        description=(
            f"Research the following topic thoroughly: '{user_topic}'. \n"
            "Use web search to find recent, accurate information. "
            "Identify at least 3 key findings with their sources. "
            "Save important context to the Semantic Vault using the Context Writer Tool."
        ),
        expected_output=(
            "A structured research summary containing: \n"
            "1. At least 3 key findings with sources \n"
            "2. Recent developments (last 12 months) \n"
            "3. Any relevant data points or statistics"
        ),
        agent=agent,
    )


def create_analysis_task(agent: Agent, user_topic: str,
                         research_task: Task) -> Task:
    """Phase 2 — Analysis: distillation and SQL grounding."""
    return Task(
        description=(
            f"Analyse the research findings on '{user_topic}'. \n"
            "Query the knowledge database for any related stored facts. "
            "Cross-reference web findings with database records. "
            "Identify patterns, gaps, and key insights. "
            "Use SUM() for any numerical aggregations — never estimate."
        ),
        expected_output=(
            "A structured analysis report containing: \n"
            "1. Key patterns and insights from the research \n"
            "2. Any grounded facts retrieved from the database \n"
            "3. Identified gaps or areas requiring caution \n"
            "4. Confidence level for each major claim (High/Medium/Low)"
        ),
        agent=agent,
        context=[research_task],
    )


def create_writing_task(agent: Agent, user_topic: str,
                        research_task: Task, analysis_task: Task) -> Task:
    """Phase 3 — Reporting: human-readable artifact generation."""
    return Task(
        description=(
            f"Write a professional report on '{user_topic}' using the research "
            "and analysis provided in context. \n"
            "Structure: Introduction → Key Findings → Analysis → Conclusion. \n"
            "Every claim must be traceable to the context provided. "
            "Target length: 400-600 words. Professional tone."
        ),
        expected_output=(
            "A complete, publication-ready report (400-600 words) with: \n"
            "1. Introduction (what and why) \n"
            "2. Key Findings (at least 3, with supporting detail) \n"
            "3. Analysis (patterns, implications) \n"
            "4. Conclusion (summary and next steps)"
        ),
        agent=agent,
        context=[research_task, analysis_task],
    )
