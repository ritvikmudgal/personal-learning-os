"""Concepts & Concept Graph API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.domain.concept import (
    ConceptCreate,
    ConceptRelationshipCreate,
    ConceptRelationshipResponse,
    ConceptResponse,
    ConceptUpdate,
)
from app.domain.graph import PrerequisiteSubgraphResponse
from app.services.graph_service import GraphService

router = APIRouter(prefix="/concepts", tags=["Concepts & Graph"])


@router.post("", response_model=ConceptResponse, status_code=status.HTTP_201_CREATED)
async def create_concept(
    data: ConceptCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new concept."""
    service = GraphService(db)
    return await service.create_concept(data)


@router.get("", response_model=list[ConceptResponse])
async def list_concepts(
    domain: str | None = Query(None, description="Filter concepts by domain"),
    db: AsyncSession = Depends(get_db_session),
):
    """List all concepts, optionally filtered by domain."""
    service = GraphService(db)
    return await service.get_all_concepts(domain=domain)


@router.get("/{concept_id}", response_model=ConceptResponse)
async def get_concept(
    concept_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get concept by ID."""
    service = GraphService(db)
    concept = await service.get_concept(concept_id)
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found",
        )
    return concept


@router.patch("/{concept_id}", response_model=ConceptResponse)
async def update_concept(
    concept_id: int,
    data: ConceptUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update concept fields."""
    service = GraphService(db)
    updated = await service.update_concept(concept_id, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found",
        )
    return updated


@router.post(
    "/relationships",
    response_model=ConceptRelationshipResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_relationship(
    data: ConceptRelationshipCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a relationship between concepts (includes cycle detection for prerequisites)."""
    service = GraphService(db)
    try:
        return await service.create_relationship(data)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )


@router.delete("/relationships/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_relationship(
    relationship_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Remove a concept relationship."""
    service = GraphService(db)
    success = await service.remove_relationship(relationship_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship {relationship_id} not found",
        )


@router.get("/{concept_id}/prerequisites", response_model=list[ConceptResponse])
async def get_direct_prerequisites(
    concept_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get direct prerequisites for a concept."""
    service = GraphService(db)
    return await service.get_direct_prerequisites(concept_id)


@router.get("/{concept_id}/dependents", response_model=list[ConceptResponse])
async def get_direct_dependents(
    concept_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get direct dependents for a concept."""
    service = GraphService(db)
    return await service.get_direct_dependents(concept_id)


@router.get("/{concept_id}/prerequisite-chain", response_model=list[ConceptResponse])
async def get_prerequisite_chain(
    concept_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get all transitive prerequisites of a concept in BFS traversal order."""
    service = GraphService(db)
    return await service.traverse_prerequisite_chain(concept_id)


@router.get(
    "/{concept_id}/prerequisite-subgraph",
    response_model=PrerequisiteSubgraphResponse,
)
async def get_prerequisite_subgraph(
    concept_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get full prerequisite DAG subgraph (nodes and edges) for a concept."""
    service = GraphService(db)
    nodes, edges = await service.get_prerequisite_subgraph(concept_id)
    return PrerequisiteSubgraphResponse(
        target_concept_id=concept_id,
        nodes=[ConceptResponse.model_validate(n) for n in nodes],
        edges=edges,
    )
