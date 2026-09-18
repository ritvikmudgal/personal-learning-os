"""Learner profile API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.repositories.learner_repo import LearnerRepository
from app.domain.learner import (
    KnowledgeStateResponse,
    LearnerCreate,
    LearnerKnowledgeSummary,
    LearnerResponse,
    LearnerUpdate,
)
from app.utils.logging import get_logger

logger = get_logger("api.learner")

router = APIRouter(prefix="/learner", tags=["learner"])


@router.post("", response_model=LearnerResponse, status_code=201)
async def create_learner(
    data: LearnerCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new learner profile."""
    repo = LearnerRepository(db)
    learner = await repo.create(data)
    return LearnerResponse.model_validate(learner)


@router.get("", response_model=list[LearnerResponse])
async def list_learners(
    db: AsyncSession = Depends(get_db_session),
):
    """List all learner profiles."""
    repo = LearnerRepository(db)
    learners = await repo.get_all()
    return [LearnerResponse.model_validate(l) for l in learners]


@router.get("/{learner_id}", response_model=LearnerResponse)
async def get_learner(
    learner_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a learner profile by ID."""
    repo = LearnerRepository(db)
    learner = await repo.get_by_id(learner_id)
    if learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    return LearnerResponse.model_validate(learner)


@router.patch("/{learner_id}", response_model=LearnerResponse)
async def update_learner(
    learner_id: int,
    data: LearnerUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update a learner profile."""
    repo = LearnerRepository(db)
    learner = await repo.update(learner_id, data)
    if learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    return LearnerResponse.model_validate(learner)


@router.delete("/{learner_id}", status_code=204)
async def delete_learner(
    learner_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a learner profile."""
    repo = LearnerRepository(db)
    deleted = await repo.delete(learner_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Learner not found")


@router.get("/{learner_id}/knowledge", response_model=LearnerKnowledgeSummary)
async def get_learner_knowledge(
    learner_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a summary of a learner's knowledge state across all concepts."""
    repo = LearnerRepository(db)

    # Verify learner exists
    learner = await repo.get_by_id(learner_id)
    if learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")

    states = await repo.get_knowledge_states(learner_id)
    state_responses = []
    for state in states:
        resp = KnowledgeStateResponse.model_validate(state)
        if state.concept:
            resp.concept_name = state.concept.name
        state_responses.append(resp)

    return LearnerKnowledgeSummary(
        learner_id=learner_id,
        total_concepts_studied=len(state_responses),
        states=state_responses,
    )
