"""Database models for persistent storage."""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class WorkflowRecordDB(BaseModel):
    """Database model for workflow records."""

    id: str
    status: str
    requirements: str
    context: str | None = None
    provider: str | None = None
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
    architect_status: str | None = None
    architect_result: str | None = None
    architect_started_at: str | None = None
    architect_completed_at: str | None = None
    architect_error: str | None = None
    implement_status: str | None = None
    implement_result: str | None = None
    implement_started_at: str | None = None
    implement_completed_at: str | None = None
    implement_error: str | None = None
    reviewer_status: str | None = None
    reviewer_result: str | None = None
    reviewer_started_at: str | None = None
    reviewer_completed_at: str | None = None
    reviewer_error: str | None = None
    tester_status: str | None = None
    tester_result: str | None = None
    tester_started_at: str | None = None
    tester_completed_at: str | None = None
    tester_error: str | None = None


class ConversationHistoryRecord(BaseModel):
    """Database model for conversation history."""

    id: int
    workflow_id: str
    agent_name: str
    role: str
    content: str
    timestamp: str


class WorkflowListItem(BaseModel):
    """Model for workflow list items."""

    workflow_id: str
    status: str
    requirements: str
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    current_step: str | None = None
    architect_status: str | None = None
    implement_status: str | None = None
    reviewer_status: str | None = None
    tester_status: str | None = None


class ConversationMessage(BaseModel):
    """Model for a single conversation message."""

    id: int
    workflow_id: str
    agent_name: str
    role: str
    content: str
    timestamp: str


class WorkflowDetail(BaseModel):
    """Detailed model for workflow with agent results."""

    workflow_id: str
    status: str
    requirements: str
    context: str | None = None
    provider: str | None = None
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
    current_step: str | None = None
    architect_status: str | None = None
    architect_result: dict[str, Any] | None = None
    implement_result: dict[str, Any] | None = None
    reviewer_result: dict[str, Any] | None = None
    tester_result: dict[str, Any] | None = None


class DashboardStats(BaseModel):
    """Statistics for the dashboard."""

    total_workflows: int
    pending_workflows: int
    running_workflows: int
    completed_workflows: int
    failed_workflows: int
