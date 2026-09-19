"""Material domain schemas for API request/response serialization (re-exports from library)."""

from app.domain.library import (
    DocumentChunkResponse,
    MaterialConceptResponse,
    MaterialDetailResponse,
    MaterialResponse,
)

__all__ = [
    "MaterialResponse",
    "MaterialDetailResponse",
    "MaterialConceptResponse",
    "DocumentChunkResponse",
]
