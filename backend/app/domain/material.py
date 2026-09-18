"""Material metadata domain schemas for API request/response serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MaterialMetadataCreate(BaseModel):
    """Schema for recording uploaded material metadata."""
    learner_id: int
    title: str = Field(..., min_length=1, max_length=500)
    file_path: Optional[str] = None
    content_type: Optional[str] = Field(None, max_length=100)
    file_size_bytes: Optional[int] = Field(None, ge=0)
    associated_concept_ids: Optional[list[int]] = None


class MaterialMetadataResponse(BaseModel):
    """Schema for material metadata API responses."""
    id: int
    learner_id: int
    title: str
    file_path: Optional[str] = None
    content_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    associated_concept_ids: Optional[list] = None
    upload_date: datetime

    model_config = {"from_attributes": True}
