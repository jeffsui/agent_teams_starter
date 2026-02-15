"""Workflow repository for database operations."""
import json
from datetime import datetime
from typing import Any

import aiosqlite

from src.app.core.database import get_db, init_db
from src.app.models import (
    WorkflowRecordDB,
    ConversationHistoryRecord,
    WorkflowListItem,
    ConversationMessage,
    WorkflowDetail,
    DashboardStats,
)
from src.app.models.orchestration import WorkflowState, AgentStepStatus


class WorkflowRepository:
    """Repository for workflow data access."""

    def __init__(self) -> None:
        """Initialize the repository."""
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Ensure database is initialized."""
        if not self._initialized:
            await init_db()
            self._initialized = True

    async def create_workflow(
        self,
        workflow_id: str,
        status: str,
        requirements: str,
        context: str | None = None,
        provider: str | None = None,
    ) -> None:
        """Create a new workflow record.

        Args:
            workflow_id: The workflow ID.
            status: The workflow status.
            requirements: User requirements.
            context: Additional context.
            provider: LLM provider.
        """
        await self._ensure_initialized()

        async with get_db() as db:
            now = datetime.utcnow().isoformat()
            await db.execute(
                """
                INSERT INTO workflows (
                    id, status, requirements, context, provider,
                    created_at, architect_status, implement_status,
                    reviewer_status, tester_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    workflow_id,
                    status,
                    requirements,
                    context,
                    provider,
                    now,
                    AgentStepStatus.PENDING,
                    AgentStepStatus.PENDING,
                    AgentStepStatus.PENDING,
                    AgentStepStatus.PENDING,
                ),
            )
            await db.commit()

    async def update_workflow_status(
        self,
        workflow_id: str,
        status: str | None = None,
        started_at: str | None = None,
        completed_at: str | None = None,
        error: str | None = None,
    ) -> None:
        """Update workflow status.

        Args:
            workflow_id: The workflow ID.
            status: New workflow status.
            started_at: Start timestamp.
            completed_at: Completion timestamp.
            error: Error message if failed.
        """
        await self._ensure_initialized()

        updates = []
        params = []

        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if started_at is not None:
            updates.append("started_at = ?")
            params.append(started_at)
        if completed_at is not None:
            updates.append("completed_at = ?")
            params.append(completed_at)
        if error is not None:
            updates.append("error = ?")
            params.append(error)

        if not updates:
            return

        params.append(workflow_id)

        async with get_db() as db:
            query = f"UPDATE workflows SET {', '.join(updates)} WHERE id = ?"
            await db.execute(query, params)
            await db.commit()

    async def update_agent_step(
        self,
        workflow_id: str,
        agent_name: str,
        status: str,
        started_at: str | None = None,
        completed_at: str | None = None,
        result: dict | None = None,
        error: str | None = None,
    ) -> None:
        """Update an agent step status.

        Args:
            workflow_id: The workflow ID.
            agent_name: The agent name (architect, implement, reviewer, tester).
            status: The step status.
            started_at: Start timestamp.
            completed_at: Completion timestamp.
            result: The result data as JSON string.
            error: Error message if failed.
        """
        await self._ensure_initialized()

        field_prefix = f"{agent_name}_"
        updates = []
        params = []

        updates.append(f"{field_prefix}status = ?")
        params.append(status)

        if started_at is not None:
            updates.append(f"{field_prefix}started_at = ?")
            params.append(started_at)
        if completed_at is not None:
            updates.append(f"{field_prefix}completed_at = ?")
            params.append(completed_at)
        if result is not None:
            updates.append(f"{field_prefix}result = ?")
            params.append(json.dumps(result))
        if error is not None:
            updates.append(f"{field_prefix}error = ?")
            params.append(error)

        params.append(workflow_id)

        async with get_db() as db:
            query = f"UPDATE workflows SET {', '.join(updates)} WHERE id = ?"
            await db.execute(query, params)
            await db.commit()

    async def get_workflow(self, workflow_id: str) -> WorkflowDetail | None:
        """Get a workflow by ID.

        Args:
            workflow_id: The workflow ID.

        Returns:
            The workflow detail, or None if not found.
        """
        await self._ensure_initialized()

        async with get_db() as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT * FROM workflows WHERE id = ?
                """,
                (workflow_id,),
            )
            row = await cursor.fetchone()

            if not row:
                return None

            return self._row_to_workflow_detail(row)

    async def list_workflows(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
    ) -> list[WorkflowListItem]:
        """List workflows with pagination and filtering.

        Args:
            limit: Maximum number of records.
            offset: Number of records to skip.
            status: Filter by status.

        Returns:
            List of workflow list items.
        """
        await self._ensure_initialized()

        async with get_db() as db:
            db.row_factory = aiosqlite.Row

            query = "SELECT * FROM workflows"
            params = []

            if status:
                query += " WHERE status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()

            return [self._row_to_workflow_list_item(row) for row in rows]

    async def get_workflow_count(self, status: str | None = None) -> int:
        """Get total count of workflows.

        Args:
            status: Filter by status.

        Returns:
            The total count.
        """
        await self._ensure_initialized()

        async with get_db() as db:
            if status:
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM workflows WHERE status = ?",
                    (status,),
                )
            else:
                cursor = await db.execute("SELECT COUNT(*) FROM workflows")

            row = await cursor.fetchone()
            return row[0] if row else 0

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow.

        Args:
            workflow_id: The workflow ID.

        Returns:
            True if deleted, False if not found.
        """
        await self._ensure_initialized()

        async with get_db() as db:
            cursor = await db.execute(
                "DELETE FROM workflows WHERE id = ?",
                (workflow_id,),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def save_conversation(
        self,
        workflow_id: str,
        agent_name: str,
        role: str,
        content: str,
    ) -> None:
        """Save a conversation message.

        Args:
            workflow_id: The workflow ID.
            agent_name: The agent name.
            role: The role (user/assistant).
            content: The message content.
        """
        await self._ensure_initialized()

        async with get_db() as db:
            now = datetime.utcnow().isoformat()
            await db.execute(
                """
                INSERT INTO conversation_history
                (workflow_id, agent_name, role, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (workflow_id, agent_name, role, content, now),
            )
            await db.commit()

    async def get_conversation_history(
        self,
        workflow_id: str,
    ) -> list[ConversationMessage]:
        """Get conversation history for a workflow.

        Args:
            workflow_id: The workflow ID.

        Returns:
            List of conversation messages.
        """
        await self._ensure_initialized()

        async with get_db() as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT * FROM conversation_history
                WHERE workflow_id = ?
                ORDER BY timestamp ASC
                """,
                (workflow_id,),
            )
            rows = await cursor.fetchall()

            return [
                ConversationMessage(
                    id=row["id"],
                    workflow_id=row["workflow_id"],
                    agent_name=row["agent_name"],
                    role=row["role"],
                    content=row["content"],
                    timestamp=row["timestamp"],
                )
                for row in rows
            ]

    async def get_dashboard_stats(self) -> DashboardStats:
        """Get dashboard statistics.

        Returns:
            Dashboard statistics.
        """
        await self._ensure_initialized()

        async with get_db() as db:
            total = await (await db.execute("SELECT COUNT(*) FROM workflows")).fetchone()
            pending = await (await db.execute("SELECT COUNT(*) FROM workflows WHERE status = 'pending'")).fetchone()
            running = await (await db.execute("SELECT COUNT(*) FROM workflows WHERE status = 'running'")).fetchone()
            completed = await (await db.execute("SELECT COUNT(*) FROM workflows WHERE status = 'completed'")).fetchone()
            failed = await (await db.execute("SELECT COUNT(*) FROM workflows WHERE status = 'failed'")).fetchone()

            return DashboardStats(
                total_workflows=total[0] if total else 0,
                pending_workflows=pending[0] if pending else 0,
                running_workflows=running[0] if running else 0,
                completed_workflows=completed[0] if completed else 0,
                failed_workflows=failed[0] if failed else 0,
            )

    def _row_to_workflow_detail(self, row: aiosqlite.Row) -> WorkflowDetail:
        """Convert a database row to WorkflowDetail.

        Args:
            row: The database row.

        Returns:
            WorkflowDetail instance.
        """
        current_step = self._get_current_step(row)

        return WorkflowDetail(
            workflow_id=row["id"],
            status=row["status"],
            requirements=row["requirements"],
            context=row["context"],
            provider=row["provider"],
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            error=row["error"],
            current_step=current_step,
            architect_status=row["architect_status"],
            architect_result=self._parse_json(row["architect_result"]),
            implement_result=self._parse_json(row["implement_result"]),
            reviewer_result=self._parse_json(row["reviewer_result"]),
            tester_result=self._parse_json(row["tester_result"]),
        )

    def _row_to_workflow_list_item(self, row: aiosqlite.Row) -> WorkflowListItem:
        """Convert a database row to WorkflowListItem.

        Args:
            row: The database row.

        Returns:
            WorkflowListItem instance.
        """
        current_step = self._get_current_step(row)

        return WorkflowListItem(
            workflow_id=row["id"],
            status=row["status"],
            requirements=row["requirements"],
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            current_step=current_step,
            architect_status=row["architect_status"],
            implement_status=row["implement_status"],
            reviewer_status=row["reviewer_status"],
            tester_status=row["tester_status"],
        )

    def _get_current_step(self, row: aiosqlite.Row) -> str | None:
        """Get the current executing step from a row.

        Args:
            row: The database row.

        Returns:
            The current step name or None.
        """
        if row["architect_status"] == AgentStepStatus.IN_PROGRESS:
            return "architect"
        elif row["implement_status"] == AgentStepStatus.IN_PROGRESS:
            return "implement"
        elif row["reviewer_status"] == AgentStepStatus.IN_PROGRESS:
            return "reviewer"
        elif row["tester_status"] == AgentStepStatus.IN_PROGRESS:
            return "tester"
        return None

    def _parse_json(self, value: str | None) -> dict | None:
        """Parse JSON string to dict.

        Args:
            value: JSON string.

        Returns:
            Parsed dict or None.
        """
        if value is None:
            return None
        try:
            return json.loads(value)
        except Exception:
            return None


# Global repository instance
_repository: WorkflowRepository | None = None


def get_workflow_repository() -> WorkflowRepository:
    """Get the global workflow repository instance.

    Returns:
        The global WorkflowRepository instance.
    """
    global _repository
    if _repository is None:
        _repository = WorkflowRepository()
    return _repository
