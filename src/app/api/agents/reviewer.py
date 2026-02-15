"""Reviewer agent API endpoint."""
from typing import Any

from fastapi import APIRouter, HTTPException, status

from src.app.core.agents import ReviewerAgent
from src.app.core.llm_providers import ProviderFactory, ProviderConfig
from src.app.models import (
    ReviewerRequest,
    ReviewerResponse,
)

router = APIRouter()


@router.post("/reviewer", response_model=ReviewerResponse)
async def run_reviewer(request: ReviewerRequest) -> ReviewerResponse:
    """Run the reviewer agent to review code implementation.

    Args:
        request: Reviewer request with implementation and context.

    Returns:
        Reviewer response with code review findings.

    Raises:
        HTTPException: If agent execution fails.
    """
    try:
        # Create provider
        config = ProviderConfig()
        if request.provider:
            config.default_provider = request.provider

        provider = ProviderFactory.create(request.provider, config)

        # Create and run agent
        agent = ReviewerAgent(provider)

        kwargs: dict[str, Any] = {"implementation": request.implementation}
        if request.architecture:
            kwargs["architecture"] = request.architecture
        if request.requirements:
            kwargs["requirements"] = request.requirements
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens

        result = await agent.execute(**kwargs)

        return ReviewerResponse(agent="reviewer", result=result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reviewer agent failed: {str(e)}",
        )
