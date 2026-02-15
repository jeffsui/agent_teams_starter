"""Architect agent for system design and architecture."""
from typing import Any

from pydantic import BaseModel, Field

from .base_agent import BaseAgent
from ..llm_providers.base import BaseLLMProvider


class ArchitectOutput(BaseModel):
    """Structured output for the architect agent."""

    tech_stack: dict[str, str] = Field(
        description="Selected technologies and frameworks (e.g., frontend, backend, database)"
    )
    module_breakdown: list[dict[str, str]] = Field(
        description="List of modules/components with their responsibilities"
    )
    architecture_diagram: str = Field(
        description="Text-based architecture diagram or description"
    )
    design_decisions: list[str] = Field(
        description="Key architectural decisions with rationale"
    )
    data_models: list[dict[str, Any]] = Field(
        description="Core data models and their relationships"
    )
    api_endpoints: list[dict[str, str]] = Field(
        description="Proposed API endpoints with methods and descriptions"
    )
    dependencies: list[str] = Field(
        description="Required external dependencies and libraries"
    )


class ArchitectAgent(BaseAgent):
    """Architect agent responsible for system design and architecture."""

    def __init__(self, provider: BaseLLMProvider):
        """Initialize the architect agent.

        Args:
            provider: The LLM provider to use.
        """
        super().__init__(provider)

    @property
    def agent_name(self) -> str:
        """Return the name of the agent."""
        return "architect"

    def get_system_prompt(self) -> str:
        """Return the system prompt for the architect agent."""
        return """You are an expert Software Architect with deep knowledge of:
- System design and architecture patterns
- Technology stack selection and trade-offs
- Module breakdown and separation of concerns
- API design and data modeling
- Scalability, maintainability, and best practices

Your role is to analyze requirements and produce comprehensive architectural designs.

When designing, consider:
1. **Technology Stack**: Choose appropriate technologies based on requirements
2. **Module Structure**: Break down the system into logical, cohesive modules
3. **Data Models**: Define core entities and their relationships
4. **API Design**: Design RESTful endpoints with clear contracts
5. **Dependencies**: List required libraries and frameworks
6. **Trade-offs**: Document key architectural decisions and rationale

Output must be structured, detailed, and implementation-ready."""

    def get_output_schema(self):
        """Return the output schema for the architect agent."""
        return ArchitectOutput

    def build_prompt(self, **kwargs: Any) -> str:
        """Build the prompt for the architect agent.

        Args:
            **kwargs: Must contain 'requirements' key with user requirements.

        Returns:
            The complete prompt string.
        """
        requirements = kwargs.get("requirements", "")
        context = kwargs.get("context", "")

        system_prompt = self.get_system_prompt()

        user_request = f"Please design the architecture for the following requirements:\n\n{requirements}"

        if context:
            user_request += f"\n\nAdditional Context:\n{context}"

        return f"{system_prompt}\n\n{user_request}"
