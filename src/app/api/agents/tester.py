"""Tester agent API endpoint."""
from typing import Any

from fastapi import APIRouter, HTTPException, status

from src.app.core.agents import TesterAgent
from src.app.core.llm_providers import ProviderFactory, ProviderConfig
from src.app.models import (
    TesterRequest,
    TesterResponse,
)

router = APIRouter()


@router.post("/tester", response_model=TesterResponse)
async def run_tester(request: TesterRequest) -> TesterResponse:
    """Run the tester agent to generate test cases.

    Args:
        request: Tester request with implementation and context.

    Returns:
        Tester response with generated test cases.

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
        agent = TesterAgent(provider)

        kwargs: dict[str, Any] = {"implementation": request.implementation}
        if request.architecture:
            kwargs["architecture"] = request.architecture
        if request.requirements:
            kwargs["requirements"] = request.requirements
        if request.review:
            kwargs["review"] = request.review
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens

        result = await agent.execute(**kwargs)

        return TesterResponse(agent="tester", result=result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tester agent failed: {str(e)}",
        )
