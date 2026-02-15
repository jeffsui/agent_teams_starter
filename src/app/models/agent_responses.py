"""Response models for agent API endpoints."""
from typing import Any

from pydantic import BaseModel

from src.app.core.agents import (
    ArchitectOutput,
    ImplementOutput,
    ReviewerOutput,
    TesterOutput,
)


class ArchitectResponse(BaseModel):
    """Response model for the architect agent."""

    agent: str = "architect"
    result: ArchitectOutput


class ImplementResponse(BaseModel):
    """Response model for the implement agent."""

    agent: str = "implement"
    result: ImplementOutput


class ReviewerResponse(BaseModel):
    """Response model for the reviewer agent."""

    agent: str = "reviewer"
    result: ReviewerOutput


class TesterResponse(BaseModel):
    """Response model for the tester agent."""

    agent: str = "tester"
    result: TesterOutput


class AgentResponse(BaseModel):
    """Generic response model for any agent."""

    agent: str
    result: dict[str, Any] | list[Any] | str | int


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str
    detail: str | None = None
    agent: str | None = None
