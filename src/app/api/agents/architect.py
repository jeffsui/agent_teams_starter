"""Architect agent API endpoint."""
from typing import Any

from fastapi import APIRouter, HTTPException, status

from src.app.core.agents import ArchitectAgent
from src.app.core.llm_providers import ProviderFactory, ProviderConfig
from src.app.models import (
    ArchitectRequest,
    ArchitectResponse,
    ErrorResponse,
)

router = APIRouter()


@router.post("/architect", response_model=ArchitectResponse)
async def run_architect(request: ArchitectRequest) -> ArchitectResponse:
    """Run the architect agent to generate system architecture.

    Args:
        request: Architect request with requirements and context.

    Returns:
        Architect response with generated architecture.

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
        agent = ArchitectAgent(provider)

        kwargs: dict[str, Any] = {"requirements": request.requirements}
        if request.context:
            kwargs["context"] = request.context
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens

        result = await agent.execute(**kwargs)

        return ArchitectResponse(agent="architect", result=result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Architect agent failed: {str(e)}",
        )
