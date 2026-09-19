"""Evidence domain schemas for API request/response serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.db.models import EvidenceType


class EvidenceCreate(BaseModel):
    """Schema for recording a piece of learning evidence."""

    concept_id: Optional[int] = None
    evidence_type: EvidenceType
    result_quality: float = Field(..., ge=0.0, le=1.0)
    difficulty: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    source: str = Field("user_interaction", max_length=255)
    misconception_info: Optional[dict] = None
    notes: Optional[str] = None


class EvidenceResponse(BaseModel):
    """Schema for learning evidence API responses."""

    id: int
    learner_id: int
    concept_id: Optional[int] = None
    evidence_type: EvidenceType
    result_quality: float
    difficulty: Optional[float] = None
    confidence: Optional[float] = None
    source: str
    misconception_info: Optional[dict] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
