"""Assessment domain schemas for API request/response serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.db.models import MisconceptionStatus


class AssessmentRecordCreate(BaseModel):
    """Schema for recording an assessment result."""

    learner_id: int
    concept_id: Optional[int] = None
    assessment_type: str  # quiz, exam, self_assessment, ai_assessment, practice_problem
    score: float = Field(..., ge=0.0)
    max_score: float = Field(..., gt=0.0)
    passed: bool = False
    misconceptions_detected: Optional[list[str]] = None


class AssessmentRecordResponse(BaseModel):
    """Schema for assessment record API responses."""

    id: int
    learner_id: int
    concept_id: Optional[int] = None
    assessment_type: str
    score: float
    max_score: float
    passed: bool
    misconceptions_detected: Optional[list] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MisconceptionCreate(BaseModel):
    """Schema for recording a misconception."""

    concept_id: Optional[int] = None
    description: str
    severity: float = Field(0.5, ge=0.0, le=1.0)


class MisconceptionUpdate(BaseModel):
    """Schema for updating/resolving a misconception."""

    severity: Optional[float] = Field(None, ge=0.0, le=1.0)
    status: Optional[MisconceptionStatus] = None
    resolution_notes: Optional[str] = None


class MisconceptionResponse(BaseModel):
    """Schema for misconception API responses."""

    id: int
    learner_id: int
    concept_id: Optional[int] = None
    description: str
    severity: float
    status: MisconceptionStatus
    detected_at: datetime
    last_observed_at: datetime
    evidence_count: int
    resolved: bool
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    model_config = {"from_attributes": True}
