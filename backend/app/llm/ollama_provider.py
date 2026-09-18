"""Ollama LLM provider — real implementation for local model inference.

Communicates with the Ollama API server at the configured base URL.
Default model: qwen2.5:3b (Q4_K_M quantization, 32K context).
"""

import json
from typing import AsyncIterator, Optional

import httpx

from app.llm.provider import (
    GenerateOptions,
    LLMProvider,
    LLMResponse,
    ModelInfo,
    ProviderHealthResult,
    ProviderStatus,
)
from app.utils.logging import get_logger

logger = get_logger("llm.ollama")


class OllamaProvider(LLMProvider):
    """LLM provider that communicates with a local Ollama instance."""

    def __init__(self, base_url: str, model: str, timeout: int = 120):
        """Initialize the Ollama provider.

        Args:
            base_url: Ollama API base URL (e.g., http://localhost:11434).
            model: Default model name (e.g., qwen2.5:3b).
            timeout: Request timeout in seconds.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "ollama"

    async def health_check(self) -> ProviderHealthResult:
        """Check if Ollama is running and the configured model is available."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Check if Ollama is reachable
                response = await client.get(f"{self._base_url}/api/tags")
                response.raise_for_status()

                data = response.json()
                models_data = data.get("models", [])

                available_models = [
                    ModelInfo(
                        name=m.get("name", "unknown"),
                        size=self._format_size(m.get("size")),
                        modified_at=m.get("modified_at"),
                        details=m.get("details"),
                    )
                    for m in models_data
                ]

                # Check if the configured model is available
                model_names = [m.name for m in available_models]
                model_available = any(
                    self._model in name for name in model_names
                )

                if model_available:
                    status = ProviderStatus.AVAILABLE
                    message = f"Ollama running, model '{self._model}' available"
                else:
                    status = ProviderStatus.UNAVAILABLE
                    message = (
                        f"Ollama running but model '{self._model}' not found. "
                        f"Available: {model_names}"
                    )

                return ProviderHealthResult(
                    provider_name=self.name,
                    status=status,
                    message=message,
                    available_models=available_models,
                    active_model=self._model if model_available else None,
                )

        except httpx.ConnectError:
            logger.warning("Cannot connect to Ollama at %s", self._base_url)
            return ProviderHealthResult(
                provider_name=self.name,
                status=ProviderStatus.UNAVAILABLE,
                message=f"Cannot connect to Ollama at {self._base_url}. Is Ollama running?",
            )
        except Exception as e:
            logger.error("Ollama health check failed: %s", str(e))
            return ProviderHealthResult(
                provider_name=self.name,
                status=ProviderStatus.ERROR,
                message=f"Health check error: {str(e)}",
            )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[GenerateOptions] = None,
    ) -> LLMResponse:
        """Generate a response using Ollama's /api/generate endpoint."""
        opts = options or GenerateOptions()

        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": opts.temperature,
                "top_p": opts.top_p,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        if opts.max_tokens:
            payload["options"]["num_predict"] = opts.max_tokens

        if opts.stop_sequences:
            payload["options"]["stop"] = opts.stop_sequences

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                return LLMResponse(
                    text=data.get("response", ""),
                    model=data.get("model", self._model),
                    provider=self.name,
                    usage={
                        "total_duration": data.get("total_duration"),
                        "eval_count": data.get("eval_count"),
                        "eval_duration": data.get("eval_duration"),
                    },
                    finish_reason=data.get("done_reason"),
                )

        except httpx.ConnectError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self._base_url}. Is Ollama running?"
            )
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Ollama API error: {e.response.status_code} {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[GenerateOptions] = None,
    ) -> AsyncIterator[str]:
        """Stream a response from Ollama token by token."""
        opts = options or GenerateOptions()

        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": opts.temperature,
                "top_p": opts.top_p,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        if opts.max_tokens:
            payload["options"]["num_predict"] = opts.max_tokens

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self._base_url}/api/generate",
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            token = data.get("response", "")
                            if token:
                                yield token
                            if data.get("done", False):
                                return

        except httpx.ConnectError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self._base_url}. Is Ollama running?"
            )

    @staticmethod
    def _format_size(size_bytes: int | None) -> str | None:
        """Format byte size to human-readable string."""
        if size_bytes is None:
            return None
        for unit in ("B", "KB", "MB", "GB"):
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
