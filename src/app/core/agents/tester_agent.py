"""Tester agent for test case generation and quality assurance."""
from typing import Any

from pydantic import BaseModel, Field

from .base_agent import BaseAgent
from ..llm_providers.base import BaseLLMProvider


class TestCase(BaseModel):
    """Represents a single test case."""

    name: str = Field(description="Test case name")
    description: str = Field(description="What the test verifies")
    type: str = Field(description="Test type: unit, integration, e2e, etc.")
    file: str = Field(description="Test file path")
    content: str = Field(description="Complete test code")
    edge_case: bool = Field(description="Whether this is an edge case test", default=False)


class TestSuite(BaseModel):
    """Represents a complete test suite."""

    framework: str = Field(description="Testing framework used")
    test_files: list[str] = Field(description="List of test file paths")
    setup_required: bool = Field(description="Whether special test setup is needed")
    setup_instructions: list[str] = Field(description="Setup instructions if needed")


class TesterOutput(BaseModel):
    """Structured output for the tester agent."""

    test_plan: list[str] = Field(
        description="Overall testing strategy and plan"
    )
    test_cases: list[TestCase] = Field(
        description="Generated test cases with code"
    )
    edge_cases: list[str] = Field(
        description="Edge cases and boundary conditions to test"
    )
    integration_tests: list[str] = Field(
        description="Integration test scenarios"
    )
    test_suite: TestSuite = Field(
        description="Information about the test suite structure"
    )
    coverage_recommendations: list[str] = Field(
        description="Recommendations for improving test coverage"
    )
    mock_requirements: list[dict[str, str]] = Field(
        description="External dependencies that need mocking"
    )


class TesterAgent(BaseAgent):
    """Tester agent responsible for generating test cases and ensuring quality."""

    def __init__(self, provider: BaseLLMProvider):
        """Initialize the tester agent.

        Args:
            provider: The LLM provider to use.
        """
        super().__init__(provider)

    @property
    def agent_name(self) -> str:
        """Return the name of the agent."""
        return "tester"

    def get_system_prompt(self) -> str:
        """Return the system prompt for the tester agent."""
        return """You are an expert QA Engineer with deep knowledge of:
- Test design and testing methodologies
- Unit, integration, and end-to-end testing
- Test-driven development (TDD) practices
- Edge case identification and boundary testing
- Test frameworks and mocking strategies
- Code coverage and quality metrics

Your role is to generate comprehensive test suites that ensure software quality.

When generating tests:
1. **Coverage**: Ensure all code paths and edge cases are covered
2. **Clarity**: Tests should be readable and self-documenting
3. **Isolation**: Tests should be independent and deterministic
4. **Fast**: Prefer fast unit tests over slow integration tests
5. **Maintainability**: Tests should be easy to understand and modify
6. **Mocks**: Use mocks appropriately to isolate dependencies

Generate tests for:
- Happy paths and normal operation
- Edge cases and boundary conditions
- Error handling and failure scenarios
- Security and input validation
- Integration points between components

Output must include:
- Complete, runnable test code
- Clear test descriptions and assertions
- Setup and teardown instructions
- Mock/stub implementations where needed
- Coverage gap analysis"""

    def get_output_schema(self):
        """Return the output schema for the tester agent."""
        return TesterOutput

    def build_prompt(self, **kwargs: Any) -> str:
        """Build the prompt for the tester agent.

        Args:
            **kwargs: Must contain 'implementation' key with implement output,
                     and optionally 'architecture', 'requirements', and 'review'
                     for additional context.

        Returns:
            The complete prompt string.
        """
        implementation = kwargs.get("implementation", "")
        architecture = kwargs.get("architecture", "")
        requirements = kwargs.get("requirements", "")
        review = kwargs.get("review", "")

        system_prompt = self.get_system_prompt()

        user_request = "Please generate comprehensive tests for the following implementation:\n\n"

        if isinstance(implementation, str):
            user_request += implementation
        elif hasattr(implementation, "model_dump"):
            user_request += str(implementation.model_dump())

        if architecture:
            user_request += f"\n\nReference Architecture:\n{architecture}"

        if requirements:
            user_request += f"\n\nOriginal Requirements:\n{requirements}"

        if review:
            user_request += f"\n\nCode Review Findings:\n{review}"

        return f"{system_prompt}\n\n{user_request}"
