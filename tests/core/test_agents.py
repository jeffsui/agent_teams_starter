"""Tests for agent implementations."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.app.core.agents import (
    ArchitectAgent,
    ImplementAgent,
    ReviewerAgent,
    TesterAgent,
)
from src.app.core.llm_providers.base import BaseLLMProvider


@pytest.mark.asyncio
async def test_architect_agent_execute(mock_provider):
    """Test architect agent execution."""
    agent = ArchitectAgent(mock_provider)

    result = await agent.execute(requirements="Build a REST API")

    assert result.tech_stack is not None
    assert isinstance(result.tech_stack, dict)
    assert result.module_breakdown is not None
    assert isinstance(result.module_breakdown, list)

    # Verify provider was called
    mock_provider.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_implement_agent_execute(mock_provider, mock_architect_output):
    """Test implement agent execution."""
    agent = ImplementAgent(mock_provider)

    result = await agent.execute(
        architecture=mock_architect_output.model_dump(),
        requirements="Build a REST API",
    )

    assert result.implementation_plan is not None
    assert isinstance(result.implementation_plan, list)
    assert result.files is not None
    assert isinstance(result.files, list)

    # Verify provider was called
    mock_provider.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_reviewer_agent_execute(mock_provider, mock_implement_output):
    """Test reviewer agent execution."""
    agent = ReviewerAgent(mock_provider)

    result = await agent.execute(
        implementation=mock_implement_output.model_dump(),
        requirements="Build a REST API",
    )

    assert result.overall_assessment is not None
    assert isinstance(result.overall_assessment, str)
    assert result.issues is not None
    assert isinstance(result.issues, list)
    assert result.code_quality_score >= 1
    assert result.code_quality_score <= 10

    # Verify provider was called
    mock_provider.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_tester_agent_execute(mock_provider, mock_implement_output):
    """Test tester agent execution."""
    agent = TesterAgent(mock_provider)

    result = await agent.execute(
        implementation=mock_implement_output.model_dump(),
        requirements="Build a REST API",
    )

    assert result.test_plan is not None
    assert isinstance(result.test_plan, list)
    assert result.test_cases is not None
    assert isinstance(result.test_cases, list)

    # Verify provider was called
    mock_provider.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_agent_execute_raw(mock_provider):
    """Test agent raw execution."""
    agent = ArchitectAgent(mock_provider)

    result = await agent.execute_raw(requirements="Build a REST API")

    assert isinstance(result, str)
    assert len(result) > 0

    # Verify provider was called
    mock_provider.generate.assert_called_once()


def test_agent_properties(mock_provider):
    """Test agent properties."""
    architect = ArchitectAgent(mock_provider)
    implement = ImplementAgent(mock_provider)
    reviewer = ReviewerAgent(mock_provider)
    tester = TesterAgent(mock_provider)

    assert architect.agent_name == "architect"
    assert implement.agent_name == "implement"
    assert reviewer.agent_name == "reviewer"
    assert tester.agent_name == "tester"

    assert architect.get_system_prompt() is not None
    assert len(architect.get_system_prompt()) > 0


def test_agent_output_schemas(mock_provider):
    """Test agent output schemas."""
    from src.app.core.agents import (
        ArchitectOutput,
        ImplementOutput,
        ReviewerOutput,
        TesterOutput,
    )

    architect = ArchitectAgent(mock_provider)
    implement = ImplementAgent(mock_provider)
    reviewer = ReviewerAgent(mock_provider)
    tester = TesterAgent(mock_provider)

    assert architect.get_output_schema() == ArchitectOutput
    assert implement.get_output_schema() == ImplementOutput
    assert reviewer.get_output_schema() == ReviewerOutput
    assert tester.get_output_schema() == TesterOutput


@pytest.mark.asyncio
async def test_agent_build_prompt(mock_provider):
    """Test agent prompt building."""
    agent = ArchitectAgent(mock_provider)

    prompt = agent.build_prompt(
        requirements="Build a REST API",
        context="Use FastAPI",
    )

    assert "Build a REST API" in prompt
    assert "Use FastAPI" in prompt
    assert "expert Software Architect" in prompt


@pytest.mark.asyncio
async def test_agent_execution_error_handling(mock_provider):
    """Test agent error handling."""
    mock_provider.generate_structured = AsyncMock(side_effect=Exception("API error"))

    agent = ArchitectAgent(mock_provider)

    with pytest.raises(RuntimeError, match="Agent architect execution failed"):
        await agent.execute(requirements="Build a REST API")
