"""Domain models and Pydantic schemas for Knowledge Ingestion and Library."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.db.models import IngestionStatus


class MaterialResponse(BaseModel):
    """Schema for material list response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    learner_id: int
    title: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    mime_type: str
    ingestion_status: IngestionStatus
    error_message: Optional[str] = None
    page_count: Optional[int] = None
    total_chunks: int = 0
    uploaded_at: datetime
    processed_at: Optional[datetime] = None


class DocumentChunkResponse(BaseModel):
    """Schema for document chunk response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_id: int
    chunk_index: int
    content: str
    clean_content: str
    start_char: int
    end_char: int
    page_number: Optional[int] = None
    section_header: Optional[str] = None
    token_count: int
    has_embedding: bool = False
    created_at: datetime


class MaterialConceptResponse(BaseModel):
    """Schema for material-concept association response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_id: int
    concept_id: int
    concept_name: str
    chunk_id: Optional[int] = None
    relevance_score: float
    extraction_method: str


class MaterialDetailResponse(MaterialResponse):
    """Schema for detailed material response including chunks and associated concepts."""
    chunks: list[DocumentChunkResponse] = []
    associated_concepts: list[MaterialConceptResponse] = []


class SemanticSearchRequest(BaseModel):
    """Request schema for semantic vector search."""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=50)
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)
    material_ids: Optional[list[int]] = None


class SearchResultResponse(BaseModel):
    """Response schema for semantic search query."""
    chunk_id: int
    material_id: int
    material_title: str
    chunk_index: int
    content: str
    clean_content: str
    page_number: Optional[int] = None
    section_header: Optional[str] = None
    similarity_score: float
