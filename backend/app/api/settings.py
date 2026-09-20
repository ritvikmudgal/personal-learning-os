"""FastAPI router for User Settings & AI Controls."""

from fastapi import APIRouter
from app.domain.settings_schemas import UserSettingsSchema
from app.utils.logging import get_logger

logger = get_logger("api.settings")

router = APIRouter(prefix="/settings", tags=["Settings"])

# In-memory settings state (persistent across app sessions)
_user_settings = UserSettingsSchema()


@router.get("", response_model=UserSettingsSchema)
async def get_settings_endpoint():
    """Get current user settings."""
    return _user_settings


@router.post("", response_model=UserSettingsSchema)
async def update_settings_endpoint(settings: UserSettingsSchema):
    """Update user settings."""
    global _user_settings
    _user_settings = settings
    logger.info("Updated user settings: %s", _user_settings.model_dump())
    return _user_settings


def get_current_user_settings() -> UserSettingsSchema:
    """Helper to access current in-memory settings."""
    return _user_settings
