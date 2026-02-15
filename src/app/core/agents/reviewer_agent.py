"""Reviewer agent for code review and quality assurance."""
from typing import Any

from pydantic import BaseModel, Field

from .base_agent import BaseAgent
from ..llm_providers.base import BaseLLMProvider


class Issue(BaseModel):
    """Represents a code issue found during review."""

    type: str = Field(description="Type of issue: bug, security, performance, style, etc.")
    severity: str = Field(description="Severity level: critical, high, medium, low")
    file: str = Field(description="File path where issue is found")
    line: int | None = Field(description="Line number if applicable", default=None)
    description: str = Field(description="Clear description of the issue")
    suggestion: str = Field(description="Recommended fix or improvement")


class ReviewerOutput(BaseModel):
    """Structured output for the reviewer agent."""

    overall_assessment: str = Field(
        description="Overall quality assessment of the code"
    )
    issues: list[Issue] = Field(
        description="List of issues found during review"
    )
    strengths: list[str] = Field(
        description="Positive aspects of the implementation"
    )
    security_concerns: list[str] = Field(
        description="Security-related concerns found"
    )
    performance_issues: list[str] = Field(
        description="Performance-related issues and suggestions"
    )
    code_quality_score: int = Field(
        description="Overall code quality score (1-10)", ge=1, le=10
    )
    recommendations: list[str] = Field(
        description="General recommendations for improvement"
    )


class ReviewerAgent(BaseAgent):
    """Reviewer agent responsible for code review and quality assurance."""

    def __init__(self, provider: BaseLLMProvider):
        """Initialize the reviewer agent.

        Args:
            provider: The LLM provider to use.
        """
        super().__init__(provider)

    @property
    def agent_name(self) -> str:
        """Return the name of the agent."""
        return "reviewer"

    def get_system_prompt(self) -> str:
        """Return the system prompt for the reviewer agent."""
        return """You are an expert Code Reviewer with deep knowledge of:
- Code quality best practices and design patterns
- Security vulnerabilities and safe coding practices
- Performance optimization and scalability
- Language-specific idioms and conventions
- Testing and debugging strategies
- Industry standards and guidelines

Your role is to thoroughly review code implementations and identify:
1. **Bugs**: Logic errors, edge cases, incorrect implementations
2. **Security Issues**: Injection vulnerabilities, authentication flaws, data exposure
3. **Performance Problems**: Inefficient algorithms, resource leaks, scalability concerns
4. **Code Quality**: Readability, maintainability, adherence to conventions
5. **Design Issues**: Violation of SOLID principles, tight coupling, poor separation of concerns

When reviewing:
- Be thorough but constructive
- Provide specific, actionable feedback
- Suggest concrete improvements
- Consider the context and requirements
- Acknowledge good practices used

Output must be detailed, actionable, and prioritized by severity."""

    def get_output_schema(self):
        """Return the output schema for the reviewer agent."""
        return ReviewerOutput

    def build_prompt(self, **kwargs: Any) -> str:
        """Build the prompt for the reviewer agent.

        Args:
            **kwargs: Must contain 'implementation' key with implement output,
                     and optionally 'architecture' and 'requirements' for context.

        Returns:
            The complete prompt string.
        """
        implementation = kwargs.get("implementation", "")
        architecture = kwargs.get("architecture", "")
        requirements = kwargs.get("requirements", "")

        system_prompt = self.get_system_prompt()

        user_request = "Please review the following implementation:\n\n"

        if isinstance(implementation, str):
            user_request += implementation
        elif hasattr(implementation, "model_dump"):
            user_request += str(implementation.model_dump())

        if architecture:
            user_request += f"\n\nReference Architecture:\n{architecture}"

        if requirements:
            user_request += f"\n\nOriginal Requirements:\n{requirements}"

        return f"{system_prompt}\n\n{user_request}"
