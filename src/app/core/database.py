"""Database initialization and connection management."""
import aiosqlite
from pathlib import Path
from typing import AsyncIterator
from contextlib import asynccontextmanager

# Database file path
DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "agent_teams.db"


@asynccontextmanager
async def get_db() -> AsyncIterator[aiosqlite.Connection]:
    """Get database connection.

    Yields:
        Database connection.
    """
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        yield db


async def init_db() -> None:
    """Initialize database schema."""
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        # Enable foreign keys
        await db.execute("PRAGMA foreign_keys = ON")

        # Create workflows table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                requirements TEXT NOT NULL,
                context TEXT,
                provider TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                error TEXT,
                architect_status TEXT,
                architect_result TEXT,
                architect_started_at TEXT,
                architect_completed_at TEXT,
                architect_error TEXT,
                implement_status TEXT,
                implement_result TEXT,
                implement_started_at TEXT,
                implement_completed_at TEXT,
                implement_error TEXT,
                reviewer_status TEXT,
                reviewer_result TEXT,
                reviewer_started_at TEXT,
                reviewer_completed_at TEXT,
                reviewer_error TEXT,
                tester_status TEXT,
                tester_result TEXT,
                tester_started_at TEXT,
                tester_completed_at TEXT,
                tester_error TEXT
            )
        """)

        # Create conversation_history table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
            )
        """)

        # Create indexes
        await db.execute("CREATE INDEX IF NOT EXISTS idx_workflow_status ON workflows(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_workflow_created ON workflows(created_at DESC)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_conversation_workflow ON conversation_history(workflow_id, timestamp)")

        await db.commit()
