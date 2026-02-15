"""Implement agent API endpoint."""
from typing import Any

from fastapi import APIRouter, HTTPException, status

from src.app.core.agents import ImplementAgent
from src.app.core.llm_providers import ProviderFactory, ProviderConfig
from src.app.models import (
    ImplementRequest,
    ImplementResponse,
)

router = APIRouter()


@router.post("/implement", response_model=ImplementResponse)
async def run_implement(request: ImplementRequest) -> ImplementResponse:
    """Run the implement agent to generate code implementation.

    Args:
        request: Implement request with architecture and requirements.

    Returns:
        Implement response with generated implementation.

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
        agent = ImplementAgent(provider)

        kwargs: dict[str, Any] = {"architecture": request.architecture}
        if request.requirements:
            kwargs["requirements"] = request.requirements
        if request.context:
            kwargs["context"] = request.context
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens

        result = await agent.execute(**kwargs)

        return ImplementResponse(agent="implement", result=result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Implement agent failed: {str(e)}",
        )
