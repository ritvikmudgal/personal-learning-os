"""Abstract LLM provider interface.

All LLM providers must implement this interface. The rest of the application
communicates ONLY through this interface, never directly with a specific provider.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Optional


class ProviderStatus(str, Enum):
    """Status of an LLM provider."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    NOT_CONFIGURED = "not_configured"
    ERROR = "error"


@dataclass
class ModelInfo:
    """Information about an available model."""
    name: str
    size: Optional[str] = None
    modified_at: Optional[str] = None
    details: Optional[dict] = None


@dataclass
class ProviderHealthResult:
    """Result of a provider health check."""
    provider_name: str
    status: ProviderStatus
    message: str = ""
    available_models: list[ModelInfo] = field(default_factory=list)
    active_model: Optional[str] = None


@dataclass
class GenerateOptions:
    """Options for text generation."""
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 0.9
    stop_sequences: list[str] = field(default_factory=list)


@dataclass
class LLMResponse:
    """Response from an LLM generation request."""
    text: str
    model: str
    provider: str
    usage: Optional[dict] = None  # token counts, timing, etc.
    finish_reason: Optional[str] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    All LLM providers (Ollama, cloud, future providers) must implement
    this interface. The application never depends on a specific provider.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this provider."""
        ...

    @abstractmethod
    async def health_check(self) -> ProviderHealthResult:
        """Check if this provider is available and functional.

        Returns:
            ProviderHealthResult with status and available models.
        """
        ...

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[GenerateOptions] = None,
    ) -> LLMResponse:
        """Generate a response from the LLM.

        Args:
            prompt: The user prompt/message.
            system_prompt: Optional system prompt for context.
            options: Generation options (temperature, etc.).

        Returns:
            LLMResponse with the generated text.
        """
        ...

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[GenerateOptions] = None,
    ) -> AsyncIterator[str]:
        """Stream a response from the LLM token by token.

        Args:
            prompt: The user prompt/message.
            system_prompt: Optional system prompt for context.
            options: Generation options (temperature, etc.).

        Yields:
            String tokens as they are generated.
        """
        ...
        # Note: 'yield' is needed to make this an async generator in implementations
