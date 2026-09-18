"""LLM provider abstraction layer.

Architecture:
    LLMProvider (abstract interface)
    ├── OllamaProvider  (local, default)
    └── CloudProvider    (remote, dormant until configured)

All application code communicates through the LLMProvider interface.
The ProviderFactory selects the active provider based on configuration.
"""
