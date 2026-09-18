"""Learning event domain schemas for API request/response serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LearningEventCreate(BaseModel):
    """Schema for recording a learning event."""
    learner_id: int
    concept_id: Optional[int] = None
    event_type: str  # study, review, practice, assessment, ai_conversation, material_read
    source: Optional[str] = Field(None, max_length=500)
    duration_seconds: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    metadata: Optional[dict] = None


class LearningEventResponse(BaseModel):
    """Schema for learning event API responses."""
    id: int
    learner_id: int
    concept_id: Optional[int] = None
    event_type: str
    source: Optional[str] = None
    duration_seconds: Optional[int] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}
