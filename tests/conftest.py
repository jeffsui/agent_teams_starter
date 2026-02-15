"""Shared fixtures for tests."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from src.app.main import create_app
from src.app.core.llm_providers.base import BaseLLMProvider
from src.app.core.agents import ArchitectOutput, ImplementOutput, ReviewerOutput, TesterOutput, CodeFile


@pytest.fixture
def app():
    """Create a test FastAPI app."""
    return create_app()


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_provider():
    """Create a mock LLM provider."""
    provider = MagicMock(spec=BaseLLMProvider)

    # Mock generate method
    provider.generate = AsyncMock(return_value="Mocked response")

    # Mock generate_structured method - using side_effect for async
    async def mock_generate_structured(prompt, schema, **kwargs):
        # Create a mock instance based on schema type
        if schema == ArchitectOutput:
            return ArchitectOutput(
                tech_stack={"python": "3.11", "framework": "fastapi"},
                module_breakdown=[{"name": "main", "purpose": "Entry point"}],
                architecture_diagram="Mock diagram",
                design_decisions=["Decision 1"],
                data_models=[{"name": "User", "fields": ["id", "name"]}],
                api_endpoints=[{"path": "/api/users", "method": "GET"}],
                dependencies=["fastapi", "uvicorn"],
            )
        elif schema == ImplementOutput:
            return ImplementOutput(
                implementation_plan=["Step 1", "Step 2"],
                files=[
                    CodeFile(
                        path="main.py",
                        content="# Mock file content",
                        language="python",
                        description="Main module",
                    )
                ],
                dependencies=["fastapi"],
                setup_instructions=["Install dependencies"],
                notes=["Note 1"],
            )
        elif schema == ReviewerOutput:
            return ReviewerOutput(
                overall_assessment="Good code quality",
                issues=[],
                strengths=["Clean code"],
                security_concerns=[],
                performance_issues=[],
                code_quality_score=8,
                recommendations=["Add more tests"],
            )
        elif schema == TesterOutput:
            from src.app.core.agents import TestCase, TestSuite
            return TesterOutput(
                test_plan=["Plan 1", "Plan 2"],
                test_cases=[
                    TestCase(
                        name="test_example",
                        description="Example test",
                        type="unit",
                        file="test_main.py",
                        content="def test_example(): pass",
                    )
                ],
                edge_cases=["Edge case 1"],
                integration_tests=["Integration test 1"],
                test_suite=TestSuite(
                    framework="pytest",
                    test_files=["test_main.py"],
                    setup_required=False,
                    setup_instructions=[],
                ),
                coverage_recommendations=["Increase coverage"],
                mock_requirements=[],
            )
        return schema()

    provider.generate_structured = AsyncMock(side_effect=mock_generate_structured)

    # Mock supports_streaming
    provider.supports_streaming = MagicMock(return_value=True)

    # Mock stream method
    async def mock_stream(prompt, **kwargs):
        yield "Mocked "
        yield "stream "
        yield "response"

    provider.stream = AsyncMock(side_effect=mock_stream)

    return provider


@pytest.fixture
def mock_architect_output():
    """Get mock architect output."""
    return ArchitectOutput(
        tech_stack={"python": "3.11", "framework": "fastapi"},
        module_breakdown=[{"name": "main", "purpose": "Entry point"}],
        architecture_diagram="Mock diagram",
        design_decisions=["Decision 1"],
        data_models=[{"name": "User", "fields": ["id", "name"]}],
        api_endpoints=[{"path": "/api/users", "method": "GET"}],
        dependencies=["fastapi", "uvicorn"],
    )


@pytest.fixture
def mock_implement_output():
    """Get mock implement output."""
    return ImplementOutput(
        implementation_plan=["Step 1", "Step 2"],
        files=[
            CodeFile(
                path="main.py",
                content="# Mock file content",
                language="python",
                description="Main module",
            )
        ],
        dependencies=["fastapi"],
        setup_instructions=["Install dependencies"],
        notes=["Note 1"],
    )
