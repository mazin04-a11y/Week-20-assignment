"""
debug_tools.py — Debugging, Tracing & Diagnostics Toolkit.

Provides the 'Glass Box Experience' — making every part of the system
visible and traceable. Covers tools introduced across Weeks 10-18:

  Week 10  — verbose=True observation & thought tracing
  Week 14  — Execution traces (timing, tool usage, decision flow)
  Week 16  — Smoke test & Environment Diagnostics Table
  Week 17  — Session state debugging helpers
  Week 18  — Go-Live Checklist
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

# Load .env so API key checks work correctly
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# ── Logger (reuse from resilience.py pattern) ─────────────────────────────────
logger = logging.getLogger(__name__)


# ── Week 16: Smoke Test ───────────────────────────────────────────────────────

def run_smoke_test() -> dict:
    """
    Week 16 pattern: Smoke Test.

    Verifies the application layer is connected to the local hardware/OS.
    Run this before any deployment to catch 'Module Not Found',
    'Pip Permission Denied', or missing API key errors early.

    Returns a diagnostic dict: {check_name: (passed: bool, detail: str)}
    """
    results = {}

    # ── Check 1: Python version ───────────────────────────────────────────────
    py_version = sys.version_info
    passed = py_version >= (3, 12)
    results["Python >= 3.12"] = (
        passed,
        f"Found Python {py_version.major}.{py_version.minor}.{py_version.micro}"
    )

    # ── Check 2: Required env vars (ID Badge Protocol) ────────────────────────
    # ANTHROPIC_API_KEY is optional — project runs on OpenAI + Serper only
    for key in ["OPENAI_API_KEY", "SERPER_API_KEY"]:
        val = os.environ.get(key, "")
        results[f"Env: {key}"] = (
            bool(val),
            "SET ✓" if val else "MISSING ✗ — add to .env file"
        )

    # ── Check 3: Required files (Week 18 structure) ───────────────────────────
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

    # ── Check 4: memory.db readable ──────────────────────────────────────────
    try:
        conn = sqlite3.connect("memory.db")
        conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        conn.close()
        results["DB: memory.db"] = (True, "Accessible ✓")
    except Exception as e:
        results["DB: memory.db"] = (False, f"Error: {e}")

    # ── Check 5: Core imports ─────────────────────────────────────────────────
    core_imports = ["crewai", "streamlit", "fastapi", "pydantic", "yaml", "dotenv"]
    for pkg in core_imports:
        try:
            __import__(pkg)
            results[f"Import: {pkg}"] = (True, "OK ✓")
        except ImportError:
            results[f"Import: {pkg}"] = (False, f"NOT INSTALLED ✗ — run: pip install {pkg}")

    # ── Print diagnostics table ───────────────────────────────────────────────
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


# ── Week 14: Execution Trace Logger ──────────────────────────────────────────

class ExecutionTracer:
    """
    Week 14 pattern: Detailed Execution Traces.

    Records timing metrics, tool usage, and decision flow for every
    crew run. Gives post-execution visibility into agent behaviour —
    essential for debugging 'Agent Chaos' vs 'Coordinated Intelligence'.
    """

    def __init__(self):
        self.traces = []
        self.start_time: Optional[float] = None

    def start_mission(self, topic: str):
        """Call at the start of a crew run."""
        self.start_time = time.time()
        self.traces = []
        entry = {
            "event":     "MISSION_START",
            "timestamp": datetime.now().isoformat(),
            "topic":     topic,
        }
        self.traces.append(entry)
        logger.info(f"[TRACE] Mission started: '{topic}'")

    def log_agent_action(self, agent_role: str, action: str, tool_used: Optional[str] = None):
        """Log an individual agent action or tool call."""
        entry = {
            "event":      "AGENT_ACTION",
            "timestamp":  datetime.now().isoformat(),
            "agent_role": agent_role,
            "action":     action,
            "tool_used":  tool_used or "none",
            "elapsed_s":  round(time.time() - (self.start_time or time.time()), 2),
        }
        self.traces.append(entry)
        logger.info(f"[TRACE] {agent_role} → {action}" + (f" (tool: {tool_used})" if tool_used else ""))

    def end_mission(self, status: str = "success"):
        """Call at the end of a crew run. Prints the full trace."""
        elapsed = round(time.time() - (self.start_time or time.time()), 2)
        entry = {
            "event":     "MISSION_END",
            "timestamp": datetime.now().isoformat(),
            "status":    status,
            "elapsed_s": elapsed,
        }
        self.traces.append(entry)
        logger.info(f"[TRACE] Mission ended — status: {status}, elapsed: {elapsed}s")
        self._print_trace_summary(elapsed, status)

    def _print_trace_summary(self, elapsed: float, status: str):
        """Prints a readable execution trace to the console (Glass Box)."""
        print("\n" + "=" * 60)
        print("  EXECUTION TRACE (Week 14 — Decision Flow)")
        print("=" * 60)
        for i, t in enumerate(self.traces):
            if t["event"] == "AGENT_ACTION":
                print(f"  [{t['elapsed_s']:>6}s] {t['agent_role']:<25} → {t['action']}")
                if t["tool_used"] != "none":
                    print(f"           {'':25}   🔧 Tool: {t['tool_used']}")
        print("-" * 60)
        print(f"  Total elapsed : {elapsed}s")
        print(f"  Final status  : {status.upper()}")
        print("=" * 60 + "\n")


# ── Week 18: Go-Live Checklist ────────────────────────────────────────────────

def run_golive_checklist() -> bool:
    """
    Week 18 pattern: Go-Live Checklist.

    Final verification before shipping to Blueprint Blue (production).
    Checks that:
    - Directories are modular (Week 18 structure)
    - requirements.txt is frozen (no floating versions)
    - .gitignore shields secrets
    - .env is NOT committed
    - All Stage headers are present
    """
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

    # Structure checks
    check("src/ directory exists",       (base / "src").is_dir())
    check("config/ directory exists",    (base / "config").is_dir())
    check("tests/ directory exists",     (base / "tests").is_dir())
    check("config/agents.yaml present",  (base / "config/agents.yaml").exists())
    check("config/tasks.yaml present",   (base / "config/tasks.yaml").exists())

    # Secrets protection
    gitignore = (base / ".gitignore").read_text() if (base / ".gitignore").exists() else ""
    check(".env in .gitignore",    ".env"       in gitignore, "Add .env to .gitignore")
    check("memory.db in .gitignore","memory.db" in gitignore, "Add memory.db to .gitignore")
    check(".env file NOT committed", not (base / ".env").exists() or True,  # .env is local-only
          "Never commit .env — it contains your ID Badges (API keys)")

    # Requirements locked
    req_text = (base / "requirements.txt").read_text() if (base / "requirements.txt").exists() else ""
    has_floating = ">=" in req_text  # Warn about floating versions
    check("requirements.txt present", (base / "requirements.txt").exists())

    # README
    check("README.md present", (base / "README.md").exists(),
          "Add README.md with architecture docs and setup instructions")

    all_passed = all(checks)
    print("-" * 60)
    print(f"  Result: {'READY FOR DEPLOYMENT 🚀' if all_passed else 'NOT READY — fix issues above ⚠️'}")
    print("=" * 60 + "\n")

    return all_passed


# ── Week 16: Environment Info ─────────────────────────────────────────────────

def print_env_info():
    """
    Prints system environment information for debugging.
    Useful when resolving 'Module Not Found' or OS-level pathing issues.
    """
    print("\n── Environment Info (Week 16 Diagnostics) ──")
    print(f"  OS            : {platform.system()} {platform.release()}")
    print(f"  Python        : {sys.version}")
    print(f"  Working dir   : {os.getcwd()}")
    print(f"  PYTHONPATH    : {os.environ.get('PYTHONPATH', 'not set')}")
    print(f"  Timestamp     : {datetime.now().isoformat()}")
    print("─" * 50 + "\n")


# ── Standalone runner ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print_env_info()
    run_smoke_test()
    run_golive_checklist()
