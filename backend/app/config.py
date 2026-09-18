"""Application configuration using Pydantic Settings.

Reads configuration from environment variables and .env files.
Never hard-codes secrets or API keys.
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root: personal-learning-os/
PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_ROOT = Path(__file__).parent.parent
DATA_DIR = BACKEND_ROOT / "data"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "Personal Learning OS"
    app_version: str = "0.1.0"
    debug: bool = False

    # --- Backend Server ---
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    # --- Database ---
    database_url: str = f"sqlite+aiosqlite:///{DATA_DIR / 'learning_os.db'}"

    # --- LLM Provider ---
    llm_provider: str = "ollama"  # "ollama" | "cloud"

    # --- Ollama ---
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    ollama_timeout: int = 120  # seconds

    # --- Cloud LLM (dormant by default) ---
    cloud_llm_provider: Optional[str] = None  # "openai" | "anthropic" | "google"
    cloud_llm_api_key: Optional[str] = None
    cloud_llm_model: Optional[str] = None
    cloud_llm_base_url: Optional[str] = None

    # --- Logging ---
    log_level: str = "INFO"

    # --- CORS ---
    cors_origins: list[str] = [
        "http://localhost:1420",   # Tauri dev server
        "http://127.0.0.1:1420",
        "tauri://localhost",       # Tauri production
        "https://tauri.localhost",
    ]


def get_settings() -> Settings:
    """Create and return application settings."""
    return Settings()
