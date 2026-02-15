"""Factory for creating LLM provider instances."""
from typing import Any

from pydantic_settings import BaseSettings

from .anthropic_provider import AnthropicConfig, AnthropicProvider
from .base import BaseLLMProvider
from .openai_provider import OpenAIConfig, OpenAIProvider


class ProviderConfig(BaseSettings):
    """Configuration for provider selection."""

    default_provider: str = "anthropic"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    anthropic_temperature: float = 0.7
    anthropic_max_tokens: int = 4096
    anthropic_timeout: float = 60.0
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 4096
    openai_timeout: float = 60.0
    openai_base_url: str | None = None

    class Config:
        env_prefix = ""
        env_file = ".env"


class ProviderFactory:
    """Factory for creating LLM provider instances."""

    _providers: dict[str, type[BaseLLMProvider]] = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
    }

    @classmethod
    def register_provider(cls, name: str, provider_class: type[BaseLLMProvider]) -> None:
        """Register a new provider.

        Args:
            name: The name to register the provider under.
            provider_class: The provider class to register.
        """
        cls._providers[name.lower()] = provider_class

    @classmethod
    def create(
        cls, provider_name: str | None = None, config: ProviderConfig | None = None
    ) -> BaseLLMProvider:
        """Create a provider instance.

        Args:
            provider_name: The name of the provider to create. Uses default from config if not provided.
            config: Optional configuration. Uses environment variables if not provided.

        Returns:
            An instance of the requested provider.

        Raises:
            ValueError: If the provider name is not recognized.
        """
        if config is None:
            config = ProviderConfig()

        name = (provider_name or config.default_provider).lower()

        if name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider: {name}. Available providers: {available}"
            )

        provider_class = cls._providers[name]

        # Create provider-specific config
        if name == "anthropic":
            provider_config = AnthropicConfig(
                anthropic_api_key=config.anthropic_api_key,
                anthropic_model=config.anthropic_model,
                anthropic_temperature=config.anthropic_temperature,
                anthropic_max_tokens=config.anthropic_max_tokens,
                anthropic_timeout=config.anthropic_timeout,
            )
        elif name == "openai":
            provider_config = OpenAIConfig(
                openai_api_key=config.openai_api_key,
                openai_model=config.openai_model,
                openai_temperature=config.openai_temperature,
                openai_max_tokens=config.openai_max_tokens,
                openai_timeout=config.openai_timeout,
                openai_base_url=config.openai_base_url,
            )
        else:
            # For custom registered providers, use generic config
            provider_config = config

        return provider_class(provider_config)  # type: ignore[arg-type]

    @classmethod
    def list_providers(cls) -> list[str]:
        """List all registered provider names.

        Returns:
            A list of registered provider names.
        """
        return list(cls._providers.keys())
