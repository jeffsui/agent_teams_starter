"""Models for workflow orchestration."""
from enum import Enum
from typing import Any
from datetime import datetime

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """Status of a workflow execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStepStatus(str, Enum):
    """Status of individual agent steps."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AgentStepResult(BaseModel):
    """Result of an individual agent step."""

    agent_name: str
    status: AgentStepStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: dict[str, Any] | None = None
    error: str | None = None


class WorkflowState(BaseModel):
    """State of a workflow execution."""

    workflow_id: str = Field(description="Unique identifier for the workflow")
    status: WorkflowStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    requirements: str
    context: str | None = None
    provider: str | None = None
    architect_result: AgentStepResult | None = None
    implement_result: AgentStepResult | None = None
    reviewer_result: AgentStepResult | None = None
    tester_result: AgentStepResult | None = None
    error: str | None = None


class WorkflowStartResponse(BaseModel):
    """Response when starting a new workflow."""

    workflow_id: str
    status: WorkflowStatus
    message: str = "Workflow started"


class WorkflowStatusResponse(BaseModel):
    """Response for workflow status queries."""

    workflow_id: str
    status: WorkflowStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    current_step: str | None = None
    error: str | None = None


class WorkflowResultsResponse(BaseModel):
    """Response for workflow results."""

    workflow_id: str
    status: WorkflowStatus
    results: dict[str, Any]
    architect_result: dict[str, Any] | None = None
    implement_result: dict[str, Any] | None = None
    reviewer_result: dict[str, Any] | None = None
    tester_result: dict[str, Any] | None = None
    completed_at: datetime | None = None
