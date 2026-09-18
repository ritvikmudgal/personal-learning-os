"""Cloud LLM provider — dormant stub for future cloud API integration.

This provider is NOT functional by default. It exists as a clean integration
point so that adding a cloud provider (OpenAI, Anthropic, Google, etc.) later
does not require rewriting the AI layer.

To activate:
1. Set LLM_PROVIDER=cloud in .env
2. Set CLOUD_LLM_PROVIDER to the provider name (openai, anthropic, google)
3. Set CLOUD_LLM_API_KEY to your API key
4. Set CLOUD_LLM_MODEL to the model name
"""

from typing import AsyncIterator, Optional

from app.llm.provider import (
    GenerateOptions,
    LLMProvider,
    LLMResponse,
    ProviderHealthResult,
    ProviderStatus,
)
from app.utils.logging import get_logger

logger = get_logger("llm.cloud")


class CloudProviderNotConfiguredError(Exception):
    """Raised when the cloud provider is used without proper configuration."""
    pass


class CloudProvider(LLMProvider):
    """Cloud LLM provider stub.

    This is intentionally dormant. When you're ready to add cloud support:
    1. Install the appropriate SDK (openai, anthropic, google-generativeai)
    2. Implement the generate/generate_stream methods
    3. The provider interface ensures the rest of the app doesn't need to change
    """

    def __init__(
        self,
        provider_name: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ):
        self._provider_name = provider_name
        self._api_key = api_key
        self._model = model
        self._base_url = base_url
        self._configured = all([provider_name, api_key, model])

    @property
    def name(self) -> str:
        return f"cloud/{self._provider_name or 'unconfigured'}"

    def _check_configured(self) -> None:
        """Raise if the provider is not configured."""
        if not self._configured:
            missing = []
            if not self._provider_name:
                missing.append("CLOUD_LLM_PROVIDER")
            if not self._api_key:
                missing.append("CLOUD_LLM_API_KEY")
            if not self._model:
                missing.append("CLOUD_LLM_MODEL")
            raise CloudProviderNotConfiguredError(
                f"Cloud LLM provider is not configured. "
                f"Missing environment variables: {', '.join(missing)}"
            )

    async def health_check(self) -> ProviderHealthResult:
        """Check if the cloud provider is configured (not if it's reachable)."""
        if not self._configured:
            return ProviderHealthResult(
                provider_name=self.name,
                status=ProviderStatus.NOT_CONFIGURED,
                message=(
                    "Cloud LLM provider is not configured. "
                    "Set CLOUD_LLM_PROVIDER, CLOUD_LLM_API_KEY, and "
                    "CLOUD_LLM_MODEL in your .env file."
                ),
            )

        # When configured, return available status
        # A real implementation would verify the API key
        return ProviderHealthResult(
            provider_name=self.name,
            status=ProviderStatus.AVAILABLE,
            message=f"Cloud provider '{self._provider_name}' configured with model '{self._model}'",
            active_model=self._model,
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[GenerateOptions] = None,
    ) -> LLMResponse:
        """Generate a response using the cloud provider.

        Currently raises CloudProviderNotConfiguredError.
        Will be implemented when cloud support is added.
        """
        self._check_configured()

        # TODO: Implement actual cloud API calls based on self._provider_name
        # This will be:
        # - openai: use openai SDK
        # - anthropic: use anthropic SDK
        # - google: use google-generativeai SDK
        raise NotImplementedError(
            f"Cloud provider '{self._provider_name}' generation is not yet implemented. "
            "This is a planned integration point."
        )

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[GenerateOptions] = None,
    ) -> AsyncIterator[str]:
        """Stream a response from the cloud provider.

        Currently raises CloudProviderNotConfiguredError.
        """
        self._check_configured()

        raise NotImplementedError(
            f"Cloud provider '{self._provider_name}' streaming is not yet implemented."
        )
        # yield is needed to satisfy the type signature in a real implementation
        yield ""  # pragma: no cover
