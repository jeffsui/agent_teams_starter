"""OpenAI LLM provider implementation."""
import os
from typing import Any, AsyncGenerator, TypeVar

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from .base import BaseLLMProvider


class OpenAIConfig(BaseSettings):
    """Configuration for OpenAI provider."""

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 4096
    openai_timeout: float = 60.0
    openai_base_url: str | None = None

    class Config:
        env_prefix = ""
        env_file = ".env"


T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, config: OpenAIConfig | None = None):
        """Initialize the OpenAI provider.

        Args:
            config: Optional configuration. Uses environment variables if not provided.
        """
        self._config = config or OpenAIConfig()
        self._model: ChatOpenAI | None = None

    @property
    def provider_name(self) -> str:
        """Return the name of the provider."""
        return "openai"

    def _get_model_instance(self) -> ChatOpenAI:
        """Get or create the ChatOpenAI instance."""
        if self._model is None:
            api_key = self._config.openai_api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment "
                    "variable or pass config.openai_api_key."
                )

            model_kwargs = {
                "model": self._config.openai_model,
                "temperature": self._config.openai_temperature,
                "max_tokens": self._config.openai_max_tokens,
                "timeout": self._config.openai_timeout,
                "api_key": api_key,
            }

            if self._config.openai_base_url:
                model_kwargs["base_url"] = self._config.openai_base_url

            self._model = ChatOpenAI(**model_kwargs)
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
