"""Implement agent for code implementation."""
from typing import Any

from pydantic import BaseModel, Field

from .base_agent import BaseAgent
from ..llm_providers.base import BaseLLMProvider


class CodeFile(BaseModel):
    """Represents a single code file."""

    path: str = Field(description="File path relative to project root")
    content: str = Field(description="Complete file content")
    language: str = Field(description="Programming language")
    description: str = Field(description="Brief description of the file's purpose")


class ImplementOutput(BaseModel):
    """Structured output for the implement agent."""

    implementation_plan: list[str] = Field(
        description="Step-by-step implementation plan"
    )
    files: list[CodeFile] = Field(
        description="Complete code files with full implementations"
    )
    dependencies: list[str] = Field(
        description="Additional dependencies required for implementation"
    )
    setup_instructions: list[str] = Field(
        description="Instructions for setting up and running the implementation"
    )
    notes: list[str] = Field(
        description="Important notes about the implementation"
    )


class ImplementAgent(BaseAgent):
    """Implement agent responsible for writing code based on designs."""

    def __init__(self, provider: BaseLLMProvider):
        """Initialize the implement agent.

        Args:
            provider: The LLM provider to use.
        """
        super().__init__(provider)

    @property
    def agent_name(self) -> str:
        """Return the name of the agent."""
        return "implement"

    def get_system_prompt(self) -> str:
        """Return the system prompt for the implement agent."""
        return """You are an expert Software Developer with deep knowledge of:
- Writing clean, maintainable, and well-documented code
- Implementing features based on architectural designs
- Best practices for software development
- Error handling, validation, and edge cases
- Testing and code quality

Your role is to implement software based on provided architectural designs.

When implementing:
1. **Code Quality**: Write clean, readable, and maintainable code
2. **Best Practices**: Follow language/framework conventions and patterns
3. **Error Handling**: Include proper error handling and validation
4. **Documentation**: Add comments where logic is not self-evident
5. **Testing**: Consider testability in your implementation
6. **Completeness**: Provide complete, working implementations

Output must include:
- Complete file contents (not snippets)
- Proper imports and dependencies
- Clear file structure and organization
- Setup and usage instructions"""

    def get_output_schema(self):
        """Return the output schema for the implement agent."""
        return ImplementOutput

    def build_prompt(self, **kwargs: Any) -> str:
        """Build the prompt for the implement agent.

        Args:
            **kwargs: Must contain 'architecture' key with architect output,
                     and optionally 'requirements' for original context.

        Returns:
            The complete prompt string.
        """
        architecture = kwargs.get("architecture", "")
        requirements = kwargs.get("requirements", "")
        context = kwargs.get("context", "")

        system_prompt = self.get_system_prompt()

        user_request = "Please implement the following architecture:\n\n"

        if isinstance(architecture, str):
            user_request += architecture
        elif hasattr(architecture, "model_dump"):
            # Handle Pydantic model input
            user_request += str(architecture.model_dump())

        if requirements:
            user_request += f"\n\nOriginal Requirements:\n{requirements}"

        if context:
            user_request += f"\n\nAdditional Context:\n{context}"

        return f"{system_prompt}\n\n{user_request}"
