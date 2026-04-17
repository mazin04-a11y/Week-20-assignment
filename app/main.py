"""
main.py — The Interface Layer (Week 17/18 FastAPI pattern).
Transitions the system from a CLI terminal to an HTTP-based service.
Follows the course API wrapper pattern: receive → initialise → kickoff → return JSON.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from src.crew import run_crew
from src.tools.database import setup_knowledge_db, save_run

# ── App initialisation ────────────────────────────────────────────────────────
app = FastAPI(
    title="AIOps Mission API",
    description="Interface Layer for the R-A-R Pipeline CrewAI service.",
    version="1.0.0",
)

# Ensure DB is ready on startup
setup_knowledge_db()


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/")
def health_check():
    return {"status": "online", "service": "AIOps Mission API"}


# ── Main kickoff endpoint (course pattern: data: dict) ────────────────────────
@app.post("/kickoff")
def kickoff(data: dict):
    # 1. Receive inputs from web request
    user_topic = data.get("user_topic", "").strip()

    if not user_topic:
        return {"status": "error", "result": "user_topic is required"}

    try:
        # 2. Initialise and trigger the logic
        result = run_crew(user_topic)

        # 3. Persist to memory.db
        save_run(user_topic=user_topic, result=result, status="success")

        # 4. Return structured JSON
        return {"status": "success", "result": result}

    except Exception as e:
        save_run(user_topic=user_topic, result=str(e), status="failed")
        return {"status": "error", "result": f"Mission Failed: {e}"}
