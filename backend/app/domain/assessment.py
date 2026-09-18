"""Assessment domain schemas for API request/response serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


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
    learner_id: int
    concept_id: Optional[int] = None
    description: str
    related_prerequisite_ids: Optional[list[int]] = None


class MisconceptionResponse(BaseModel):
    """Schema for misconception API responses."""
    id: int
    learner_id: int
    concept_id: Optional[int] = None
    description: str
    detected_at: datetime
    resolved: bool
    resolved_at: Optional[datetime] = None
    related_prerequisite_ids: Optional[list] = None

    model_config = {"from_attributes": True}
