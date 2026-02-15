"""Base LLM provider interface."""
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider."""
        pass

    @abstractmethod
    def get_model(self) -> Runnable:
        """Get the underlying LangChain model instance."""
        pass

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a response from the given prompt.

        Args:
            prompt: The input prompt.
            **kwargs: Additional model-specific parameters.

        Returns:
            The generated text response.
        """
        pass

    @abstractmethod
    async def generate_structured(
        self, prompt: str, schema: type[T], **kwargs: Any
    ) -> T:
        """Generate a structured response using the given Pydantic schema.

        Args:
            prompt: The input prompt.
            schema: The Pydantic model class for structured output.
            **kwargs: Additional model-specific parameters.

        Returns:
            An instance of the schema type with generated data.
        """
        pass

    @abstractmethod
    def supports_streaming(self) -> bool:
        """Check if the provider supports streaming responses.

        Returns:
            True if streaming is supported, False otherwise.
        """
        pass

    @abstractmethod
    async def stream(self, prompt: str, **kwargs: Any):
        """Stream responses from the given prompt.

        Args:
            prompt: The input prompt.
            **kwargs: Additional model-specific parameters.

        Yields:
            Chunks of the generated response.
        """
        pass
