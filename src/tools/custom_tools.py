"""
custom_tools.py — Safety-First Custom Tooling.
Follows the Week 7 & 14 BaseTool pattern with Layer 2 Guardrails.
All tools inherit from BaseTool for strict type-checking (course standard).
"""

## ---- Stage 3: Safety-First Custom Tooling (Weeks 7 & 14) ----
import sqlite3
import requests
from crewai.tools import BaseTool


# ── Tool 1: SafeQueryTool ─────────────────────────────────────────────────────
class SafeQueryTool(BaseTool):
    """
    Executes read-only SQL queries against memory.db.
    Implements Layer 2 Guardrails to prevent structural collapse and
    Denial of Wallet attacks from destructive SQL commands.
    """
    name: str = "Database Query Tool"
    description: str = (
        "Executes read-only SQL queries to fetch grounded facts from the "
        "knowledge database. Use this when you need exact numerical facts, "
        "counts, or structured data. Do NOT guess — query the database."
    )

    def _run(self, query: str) -> str:
        # ---- Safety Safeguard Pattern (Week 14) ----
        # Prevents destructive commands: DROP, DELETE, UPDATE, INSERT
        if any(keyword in query.upper() for keyword in ['DROP', 'DELETE', 'UPDATE', 'INSERT']):
            raise ValueError("Action Prohibited: Read Only Access")

        try:
            conn    = sqlite3.connect("memory.db")   # The Agent's Hard Drive
            cursor  = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            return f"Retrieved data: {results}"
        except Exception as e:
            return f"Database Error: {e}"


# ── Tool 2: WebScraperTool ────────────────────────────────────────────────────
class WebScraperTool(BaseTool):
    """
    Lightweight web content fetcher.
    Implements Immune System pattern — returns error string on failure
    rather than crashing the agent loop.
    """
    name: str = "Web Scraper Tool"
    description: str = (
        "Fetches the raw text content of a given URL. Use this to retrieve "
        "specific web pages when SerperDevTool search results aren't enough."
    )

    def _run(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            # Return first 3000 chars to stay within context window limits
            return response.text[:3000]
        except requests.exceptions.RequestException as e:
            return f"Scrape Error: {e}"


# ── Tool 3: ContextWriterTool ─────────────────────────────────────────────────
class ContextWriterTool(BaseTool):
    """
    Writes agent findings to context_notes.txt (The Semantic Vault).
    Enables persistent qualitative memory across crew runs.
    """
    name: str = "Context Writer Tool"
    description: str = (
        "Appends a note or finding to context_notes.txt for persistent "
        "qualitative memory. Use this to save important discoveries that "
        "future agents should know about."
    )

    def _run(self, note: str) -> str:
        try:
            with open("context_notes.txt", "a", encoding="utf-8") as f:
                f.write(f"\n{note}\n")
            return "Note saved to Semantic Vault (context_notes.txt)."
        except Exception as e:
            return f"Write Error: {e}"


# ── Instantiate tools for import ──────────────────────────────────────────────
sql_tool            = SafeQueryTool()
web_scraper_tool    = WebScraperTool()
context_writer_tool = ContextWriterTool()
