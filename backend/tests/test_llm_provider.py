"""Tests for the LLM provider abstraction."""

import pytest

from app.llm.provider import (
    GenerateOptions,
    LLMResponse,
    ProviderHealthResult,
    ProviderStatus,
)
from app.llm.ollama_provider import OllamaProvider
from app.llm.cloud_provider import CloudProvider, CloudProviderNotConfiguredError
from app.llm.factory import get_provider, reset_providers


class TestOllamaProvider:
    """Tests for the Ollama provider."""

    def test_provider_name(self):
        """Test that the Ollama provider has the correct name."""
        provider = OllamaProvider(
            base_url="http://localhost:11434",
            model="qwen2.5:3b",
        )
        assert provider.name == "ollama"

    @pytest.mark.asyncio
    async def test_health_check_structure(self):
        """Test that health check returns proper structure even if Ollama is down."""
        provider = OllamaProvider(
            base_url="http://localhost:11434",
            model="qwen2.5:3b",
        )
        result = await provider.health_check()
        assert isinstance(result, ProviderHealthResult)
        assert result.provider_name == "ollama"
        assert isinstance(result.status, ProviderStatus)

    @pytest.mark.asyncio
    async def test_health_check_unreachable(self):
        """Test health check when Ollama is not reachable."""
        provider = OllamaProvider(
            base_url="http://localhost:99999",  # Bad port
            model="test-model",
        )
        result = await provider.health_check()
        assert result.status in (ProviderStatus.UNAVAILABLE, ProviderStatus.ERROR)


class TestCloudProvider:
    """Tests for the cloud provider stub."""

    def test_unconfigured_name(self):
        """Test the unconfigured cloud provider name."""
        provider = CloudProvider()
        assert "unconfigured" in provider.name

    def test_configured_name(self):
        """Test the configured cloud provider name."""
        provider = CloudProvider(
            provider_name="openai",
            api_key="test-key",
            model="gpt-4",
        )
        assert "openai" in provider.name

    @pytest.mark.asyncio
    async def test_health_check_unconfigured(self):
        """Test health check returns NOT_CONFIGURED when unconfigured."""
        provider = CloudProvider()
        result = await provider.health_check()
        assert result.status == ProviderStatus.NOT_CONFIGURED

    @pytest.mark.asyncio
    async def test_health_check_configured(self):
        """Test health check returns AVAILABLE when configured."""
        provider = CloudProvider(
            provider_name="openai",
            api_key="test-key",
            model="gpt-4",
        )
        result = await provider.health_check()
        assert result.status == ProviderStatus.AVAILABLE

    @pytest.mark.asyncio
    async def test_generate_unconfigured_raises(self):
        """Test that generate raises when unconfigured."""
        provider = CloudProvider()
        with pytest.raises(CloudProviderNotConfiguredError):
            await provider.generate("test prompt")

    @pytest.mark.asyncio
    async def test_generate_configured_raises_not_implemented(self):
        """Test that generate raises NotImplementedError when configured."""
        provider = CloudProvider(
            provider_name="openai",
            api_key="test-key",
            model="gpt-4",
        )
        with pytest.raises(NotImplementedError):
            await provider.generate("test prompt")


class TestProviderFactory:
    """Tests for the provider factory."""

    def setup_method(self):
        """Reset providers before each test."""
        reset_providers()

    def test_default_provider_is_ollama(self):
        """Test that the default provider is Ollama."""
        provider = get_provider()
        assert provider.name == "ollama"

    def test_provider_is_cached(self):
        """Test that the factory returns the same instance."""
        provider1 = get_provider()
        provider2 = get_provider()
        assert provider1 is provider2

    def test_reset_clears_cache(self):
        """Test that reset allows a new instance to be created."""
        provider1 = get_provider()
        reset_providers()
        provider2 = get_provider()
        assert provider1 is not provider2
