"""Request models for agent API endpoints."""
from typing import Any

from pydantic import BaseModel, Field


class ArchitectRequest(BaseModel):
    """Request model for the architect agent."""

    requirements: str = Field(
        description="User requirements for the system to be designed",
        min_length=10,
    )
    context: str | None = Field(
        description="Additional context or constraints",
        default=None,
    )
    provider: str | None = Field(
        description="LLM provider to use (anthropic, openai)",
        default=None,
    )
    temperature: float | None = Field(
        description="Temperature for generation (0.0 - 1.0)",
        default=None,
        ge=0.0,
        le=1.0,
    )
    max_tokens: int | None = Field(
        description="Maximum tokens to generate",
        default=None,
        ge=1,
    )


class ImplementRequest(BaseModel):
    """Request model for the implement agent."""

    architecture: dict[str, Any] | str = Field(
        description="Architecture design from architect agent",
    )
    requirements: str | None = Field(
        description="Original requirements for context",
        default=None,
    )
    context: str | None = Field(
        description="Additional context or constraints",
        default=None,
    )
    provider: str | None = Field(
        description="LLM provider to use (anthropic, openai)",
        default=None,
    )
    temperature: float | None = Field(
        description="Temperature for generation (0.0 - 1.0)",
        default=None,
        ge=0.0,
        le=1.0,
    )
    max_tokens: int | None = Field(
        description="Maximum tokens to generate",
        default=None,
        ge=1,
    )


class ReviewerRequest(BaseModel):
    """Request model for the reviewer agent."""

    implementation: dict[str, Any] | str = Field(
        description="Implementation from implement agent",
    )
    architecture: dict[str, Any] | str | None = Field(
        description="Architecture design for reference",
        default=None,
    )
    requirements: str | None = Field(
        description="Original requirements for context",
        default=None,
    )
    provider: str | None = Field(
        description="LLM provider to use (anthropic, openai)",
        default=None,
    )
    temperature: float | None = Field(
        description="Temperature for generation (0.0 - 1.0)",
        default=None,
        ge=0.0,
        le=1.0,
    )
    max_tokens: int | None = Field(
        description="Maximum tokens to generate",
        default=None,
        ge=1,
    )


class TesterRequest(BaseModel):
    """Request model for the tester agent."""

    implementation: dict[str, Any] | str = Field(
        description="Implementation from implement agent",
    )
    architecture: dict[str, Any] | str | None = Field(
        description="Architecture design for reference",
        default=None,
    )
    requirements: str | None = Field(
        description="Original requirements for context",
        default=None,
    )
    review: dict[str, Any] | str | None = Field(
        description="Review findings for additional context",
        default=None,
    )
    provider: str | None = Field(
        description="LLM provider to use (anthropic, openai)",
        default=None,
    )
    temperature: float | None = Field(
        description="Temperature for generation (0.0 - 1.0)",
        default=None,
        ge=0.0,
        le=1.0,
    )
    max_tokens: int | None = Field(
        description="Maximum tokens to generate",
        default=None,
        ge=1,
    )


class WorkflowRequest(BaseModel):
    """Request model for starting a workflow."""

    requirements: str = Field(
        description="User requirements for the system",
        min_length=10,
    )
    context: str | None = Field(
        description="Additional context or constraints",
        default=None,
    )
    provider: str | None = Field(
        description="LLM provider to use for all agents (anthropic, openai)",
        default=None,
    )
    temperature: float | None = Field(
        description="Temperature for generation (0.0 - 1.0)",
        default=None,
        ge=0.0,
        le=1.0,
    )
    max_tokens: int | None = Field(
        description="Maximum tokens to generate",
        default=None,
        ge=1,
    )
