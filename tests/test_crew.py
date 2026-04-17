"""
tests/test_crew.py — Unit and integration tests.
Week 18 compliance: validate config, tools, and DB before deployment.
"""
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
import yaml
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Stage header tests ────────────────────────────────────────────────────────

def test_agents_config_loads():
    """All three agents must be defined in config/agents.yaml."""
    config_path = Path(__file__).parent.parent / "config" / "agents.yaml"
    assert config_path.exists(), "agents.yaml must exist in config/"
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    for agent in ["researcher", "analyst", "writer"]:
        assert agent in cfg, f"agents.yaml must define '{agent}'"
        assert "role"      in cfg[agent]
        assert "goal"      in cfg[agent]
        assert "backstory" in cfg[agent]


def test_tasks_config_loads():
    """All three tasks must be defined in config/tasks.yaml."""
    config_path = Path(__file__).parent.parent / "config" / "tasks.yaml"
    assert config_path.exists(), "tasks.yaml must exist in config/"
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    for task in ["research_task", "analysis_task", "writing_task"]:
        assert task in cfg, f"tasks.yaml must define '{task}'"
        assert "description"     in cfg[task]
        assert "expected_output" in cfg[task]


def test_task_descriptions_accept_user_topic():
    """All task descriptions must support {user_topic} placeholder."""
    config_path = Path(__file__).parent.parent / "config" / "tasks.yaml"
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    topic = "test topic"
    for task_name, task_cfg in cfg.items():
        formatted = task_cfg["description"].format(user_topic=topic)
        assert topic in formatted, f"{task_name} must support {{user_topic}} placeholder"


def test_project_structure():
    """Week 18 Blueprint Blue structure must be intact."""
    base = Path(__file__).parent.parent
    required = [
        "src/crew.py",
        "src/tools/custom_tools.py",
        "src/tools/database.py",
        "src/agents/research_agents.py",
        "src/tasks/research_tasks.py",
        "config/agents.yaml",
        "config/tasks.yaml",
        "app/streamlit_app.py",
        "app/main.py",
        "requirements.txt",
        "pyproject.toml",
        "README.md",
        ".env.example",
        ".gitignore",
        "Dockerfile",
        "Jenkinsfile",
    ]
    for path in required:
        assert (base / path).exists(), f"Missing required file: {path}"


def test_safe_query_tool_blocks_destructive_queries():
    """SafeQueryTool must raise ValueError on DROP/DELETE/UPDATE/INSERT."""
    from src.tools.custom_tools import SafeQueryTool
    tool = SafeQueryTool()
    for dangerous in ["DROP TABLE users", "DELETE FROM logs", "UPDATE items SET x=1", "INSERT INTO t VALUES (1)"]:
        with pytest.raises(ValueError, match="Action Prohibited"):
            tool._run(dangerous)


def test_database_setup_creates_tables():
    """setup_knowledge_db must create all required tables in memory.db."""
    from src.tools.database import setup_knowledge_db
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        setup_knowledge_db(db_path=db_path)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        assert "research_findings" in tables
        assert "run_history"       in tables
        assert "knowledge_items"   in tables
    finally:
        os.unlink(db_path)


def test_gitignore_protects_secrets():
    """.env and memory.db must be gitignored."""
    gitignore = Path(__file__).parent.parent / ".gitignore"
    content = gitignore.read_text()
    assert ".env"       in content, ".env must be in .gitignore"
    assert "memory.db"  in content, "memory.db must be in .gitignore"
