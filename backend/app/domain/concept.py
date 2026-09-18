"""Concept domain schemas for API request/response serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConceptCreate(BaseModel):
    """Schema for creating a new concept."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    domain: Optional[str] = Field(None, max_length=255)
    difficulty_level: Optional[str] = None  # beginner, intermediate, advanced, expert


class ConceptResponse(BaseModel):
    """Schema for concept API responses."""
    id: int
    name: str
    description: Optional[str] = None
    domain: Optional[str] = None
    difficulty_level: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConceptRelationshipCreate(BaseModel):
    """Schema for creating a relationship between concepts."""
    source_concept_id: int
    target_concept_id: int
    relationship_type: str  # prerequisite, related, part_of, builds_on, contrasts
    strength: float = Field(1.0, ge=0.0, le=1.0)


class ConceptRelationshipResponse(BaseModel):
    """Schema for concept relationship API responses."""
    id: int
    source_concept_id: int
    target_concept_id: int
    relationship_type: str
    strength: float
    created_at: datetime

    model_config = {"from_attributes": True}
