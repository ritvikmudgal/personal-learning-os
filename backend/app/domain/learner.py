"""Learner domain schemas for API request/response serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LearnerCreate(BaseModel):
    """Schema for creating a new learner profile."""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    preferences: Optional[dict] = Field(default_factory=dict)


class LearnerUpdate(BaseModel):
    """Schema for updating a learner profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    preferences: Optional[dict] = None


class LearnerResponse(BaseModel):
    """Schema for learner profile API responses."""
    id: int
    name: str
    email: Optional[str] = None
    preferences: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeStateResponse(BaseModel):
    """Schema for a single knowledge state entry."""
    id: int
    concept_id: int
    concept_name: Optional[str] = None
    understanding_level: float
    confidence: float
    demonstrated_level: float
    decay_factor: float
    last_assessed_at: Optional[datetime] = None
    last_studied_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LearnerKnowledgeSummary(BaseModel):
    """Summary of a learner's knowledge state across all concepts."""
    learner_id: int
    total_concepts_studied: int
    states: list[KnowledgeStateResponse]
