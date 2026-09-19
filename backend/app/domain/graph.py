"""Graph domain schemas for concept graph operations and gap analysis."""

from typing import Optional
from pydantic import BaseModel

from app.domain.concept import ConceptResponse


class PrerequisiteEdgeResponse(BaseModel):
    """Prerequisite relationship edge (source is prerequisite for target)."""

    source_concept_id: int
    target_concept_id: int


class ConceptGapInfoResponse(BaseModel):
    """Evaluated status for a prerequisite concept in gap analysis."""

    concept_id: int
    concept_name: str
    effective_mastery: float
    classification: str  # strong, moderate, weak, unknown
    mastery_probability: float
    forgetting_state: float
    confidence: float
    depth: int


class GapAnalysisResponse(BaseModel):
    """Complete gap analysis result for a target concept."""

    target_concept_id: int
    target_concept_name: str
    prerequisites: list[ConceptGapInfoResponse]
    weak_prerequisites: list[ConceptGapInfoResponse]
    prerequisite_edges: list[tuple[int, int]]
    has_gaps: bool


class PrerequisiteSubgraphResponse(BaseModel):
    """Subgraph of prerequisites for a concept."""

    target_concept_id: int
    nodes: list[ConceptResponse]
    edges: list[tuple[int, int]]
