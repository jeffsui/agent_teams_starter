"""Base agent class for all agent implementations."""
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

from ..llm_providers.base import BaseLLMProvider


T = TypeVar("T", bound=BaseModel)


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, provider: BaseLLMProvider):
        """Initialize the agent.

        Args:
            provider: The LLM provider to use for generating responses.
        """
        self._provider = provider

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Return the name of the agent."""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent.

        Returns:
            The system prompt string.
        """
        pass

    @abstractmethod
    def get_output_schema(self) -> type[T]:
        """Return the Pydantic schema for structured output.

        Returns:
            The Pydantic model class for structured output.
        """
        pass

    def build_prompt(self, **kwargs: Any) -> str:
        """Build the full prompt from system prompt and user input.

        Args:
            **kwargs: Arbitrary keyword arguments for prompt construction.

        Returns:
            The complete prompt string.
        """
        system_prompt = self.get_system_prompt()

        # Get user input from kwargs (typically 'requirements' or 'input')
        user_input = kwargs.get("requirements") or kwargs.get("input") or ""

        # Combine system prompt with user input
        if user_input:
            return f"{system_prompt}\n\nUser Request:\n{user_input}"
        return system_prompt

    async def execute(self, **kwargs: Any) -> T:
        """Execute the agent with the given input.

        Args:
            **kwargs: Arbitrary keyword arguments including requirements/input.

        Returns:
            An instance of the output schema with generated data.

        Raises:
            Exception: If generation fails.
        """
        prompt = self.build_prompt(**kwargs)
        schema = self.get_output_schema()

        try:
            result = await self._provider.generate_structured(
                prompt=prompt, schema=schema, **kwargs
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Agent {self.agent_name} execution failed: {e}") from e

    async def execute_raw(self, **kwargs: Any) -> str:
        """Execute the agent and return raw text output.

        Args:
            **kwargs: Arbitrary keyword arguments including requirements/input.

        Returns:
            The generated text response.
        """
        prompt = self.build_prompt(**kwargs)

        try:
            result = await self._provider.generate(prompt=prompt, **kwargs)
            return result
        except Exception as e:
            raise RuntimeError(f"Agent {self.agent_name} execution failed: {e}") from e
