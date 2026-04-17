"""
database.py — The Relational Foundation.
SQLite setup following the Week 14 pattern.
memory.db acts as the agent's persistent "hard drive".
"""

## ---- Stage 2: The Relational Foundation (Week 14) ----
import sqlite3


def setup_knowledge_db(db_path: str = "memory.db") -> None:
    """
    Initialises memory.db with the core knowledge schema.
    Uses CREATE TABLE IF NOT EXISTS so it is safe to call on every startup.
    """
    conn   = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ── Table 1: Research findings (Relational Memory) ────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_findings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            topic       TEXT    NOT NULL,
            finding     TEXT    NOT NULL,
            source      TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Table 2: Agent run history (Audit trail) ──────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS run_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_topic  TEXT    NOT NULL,
            result      TEXT,
            status      TEXT    DEFAULT 'pending',
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Table 3: Knowledge items (Mission-specific facts) ─────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT    NOT NULL,
            item        TEXT    NOT NULL,
            value       REAL,
            metadata    TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("── Database initialised: memory.db (The Agent's Hard Drive) ──")


def save_run(user_topic: str, result: str, status: str = "success",
             db_path: str = "memory.db") -> None:
    """Persists a crew run result to the run_history table."""
    try:
        conn   = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO run_history (user_topic, result, status) VALUES (?, ?, ?)",
            (user_topic, result, status)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Error saving run: {e}")


if __name__ == "__main__":
    setup_knowledge_db()
