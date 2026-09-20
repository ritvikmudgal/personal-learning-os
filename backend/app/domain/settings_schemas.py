"""Pydantic schemas for User Settings & AI Controls."""

from typing import Literal
from pydantic import BaseModel, Field


class UserSettingsSchema(BaseModel):
    """User settings data model."""

    local_ai_enabled: bool = Field(
        default=True,
        description="Whether local Ollama AI model is enabled for reasoning",
    )
    ai_provider_preference: Literal["auto", "local", "cloud"] = Field(
        default="auto",
        description="AI provider selection mode: 'auto', 'local', or 'cloud'",
    )
    performance_mode: Literal["cpu_friendly", "standard"] = Field(
        default="cpu_friendly",
        description="Performance mode: 'cpu_friendly' (low latency/low CPU) or 'standard'",
    )
