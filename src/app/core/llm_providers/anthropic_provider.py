"""Anthropic LLM provider implementation."""
import os
from typing import Any, AsyncGenerator, TypeVar

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from .base import BaseLLMProvider


class AnthropicConfig(BaseSettings):
    """Configuration for Anthropic provider."""

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    anthropic_temperature: float = 0.7
    anthropic_max_tokens: int = 4096
    anthropic_timeout: float = 60.0

    class Config:
        env_prefix = ""
        env_file = ".env"


T = TypeVar("T", bound=BaseModel)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider."""

    def __init__(self, config: AnthropicConfig | None = None):
        """Initialize the Anthropic provider.

        Args:
            config: Optional configuration. Uses environment variables if not provided.
        """
        self._config = config or AnthropicConfig()
        self._model: ChatAnthropic | None = None

    @property
    def provider_name(self) -> str:
        """Return the name of the provider."""
        return "anthropic"

    def _get_model_instance(self) -> ChatAnthropic:
        """Get or create the ChatAnthropic instance."""
        if self._model is None:
            api_key = self._config.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "Anthropic API key not found. Set ANTHROPIC_API_KEY environment "
                    "variable or pass config.anthropic_api_key."
                )

            self._model = ChatAnthropic(
                model=self._config.anthropic_model,
                temperature=self._config.anthropic_temperature,
                max_tokens=self._config.anthropic_max_tokens,
                timeout=self._config.anthropic_timeout,
                api_key=api_key,
            )
        return self._model

    def get_model(self) -> Runnable:
        """Get the underlying LangChain model instance."""
        return self._get_model_instance()

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a response from the given prompt."""
        model = self._get_model_instance()

        # Update model config from kwargs if provided
        if "temperature" in kwargs:
            model.temperature = kwargs["temperature"]
        if "max_tokens" in kwargs:
            model.max_tokens = kwargs["max_tokens"]

        response: AIMessage = await model.ainvoke(prompt)
        return response.content

    async def generate_structured(
        self, prompt: str, schema: type[T], **kwargs: Any
    ) -> T:
        """Generate a structured response using the given Pydantic schema."""
        model = self._get_model_instance()

        # Update model config from kwargs if provided
        if "temperature" in kwargs:
            model.temperature = kwargs["temperature"]
        if "max_tokens" in kwargs:
            model.max_tokens = kwargs["max_tokens"]

        # Use with_structured_output for structured generation
        structured_model = model.with_structured_output(schema)
        result = await structured_model.ainvoke(prompt)

        if isinstance(result, BaseModel):
            return result
        # Some providers may return dict, convert to schema
        return schema(**result)

    def supports_streaming(self) -> bool:
        """Check if the provider supports streaming responses."""
        return True

    async def stream(self, prompt: str, **kwargs: Any) -> AsyncGenerator[str, None]:
        """Stream responses from the given prompt."""
        model = self._get_model_instance()

        # Update model config from kwargs if provided
        if "temperature" in kwargs:
            model.temperature = kwargs["temperature"]
        if "max_tokens" in kwargs:
            model.max_tokens = kwargs["max_tokens"]

        async for chunk in model.astream(prompt):
            if hasattr(chunk, "content"):
                yield chunk.content
            elif isinstance(chunk, str):
                yield chunk
