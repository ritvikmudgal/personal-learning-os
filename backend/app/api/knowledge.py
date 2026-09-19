"""Learner Knowledge & Engine API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.domain.assessment import (
    MisconceptionCreate,
    MisconceptionResponse,
    MisconceptionUpdate,
)
from app.domain.evidence import EvidenceCreate, EvidenceResponse
from app.domain.graph import ConceptGapInfoResponse, GapAnalysisResponse
from app.domain.learner import KnowledgeStateResponse, LearnerKnowledgeSummary
from app.engine.decay_service import compute_effective_mastery
from app.engine.gap_analysis import find_learning_gaps
from app.services.evidence_service import EvidenceService
from app.services.learner_state_service import LearnerStateService
from app.services.misconception_service import MisconceptionService

router = APIRouter(prefix="/learner", tags=["Learner Knowledge & Engine"])


@router.get("/{learner_id}/state/{concept_id}", response_model=KnowledgeStateResponse)
async def get_learner_concept_state(
    learner_id: int,
    concept_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get multi-dimensional learner state for a concept with decay applied."""
    service = LearnerStateService(db)
    state = await service.get_current_state(learner_id, concept_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge state for learner {learner_id} and concept {concept_id} not found",
        )

    effective = compute_effective_mastery(state)
    resp = KnowledgeStateResponse.model_validate(state)
    resp.effective_mastery = round(effective, 4)
    if state.concept:
        resp.concept_name = state.concept.name
    return resp


@router.get("/{learner_id}/states", response_model=LearnerKnowledgeSummary)
async def get_all_learner_states(
    learner_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get all knowledge states for a learner."""
    service = LearnerStateService(db)
    states = await service.get_all_states(learner_id)

    state_responses = []
    for s in states:
        eff = compute_effective_mastery(s)
        res = KnowledgeStateResponse.model_validate(s)
        res.effective_mastery = round(eff, 4)
        if s.concept:
            res.concept_name = s.concept.name
        state_responses.append(res)

    return LearnerKnowledgeSummary(
        learner_id=learner_id,
        total_concepts_studied=len(states),
        states=state_responses,
    )


@router.post(
    "/{learner_id}/evidence",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_evidence(
    learner_id: int,
    data: EvidenceCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Record learning evidence and automatically update learner knowledge state."""
    service = EvidenceService(db)
    evidence, _ = await service.record_evidence(
        learner_id=learner_id,
        concept_id=data.concept_id,
        evidence_type=data.evidence_type,
        result_quality=data.result_quality,
        difficulty=data.difficulty,
        confidence=data.confidence,
        source=data.source,
        misconception_info=data.misconception_info,
        notes=data.notes,
    )
    return evidence


@router.get("/{learner_id}/evidence/{concept_id}", response_model=list[EvidenceResponse])
async def get_evidence_history(
    learner_id: int,
    concept_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Get history of evidence records for a learner-concept pair."""
    service = EvidenceService(db)
    return await service.get_recent_evidence(learner_id, concept_id, limit=limit)


@router.post(
    "/{learner_id}/misconceptions",
    response_model=MisconceptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_misconception(
    learner_id: int,
    data: MisconceptionCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Record a misconception for a learner."""
    service = MisconceptionService(db)
    return await service.record_misconception(
        learner_id=learner_id,
        description=data.description,
        concept_id=data.concept_id,
        severity=data.severity,
    )


@router.get("/{learner_id}/misconceptions", response_model=list[MisconceptionResponse])
async def list_active_misconceptions(
    learner_id: int,
    concept_id: int | None = Query(None, description="Optional concept ID filter"),
    db: AsyncSession = Depends(get_db_session),
):
    """List active misconceptions for a learner."""
    service = MisconceptionService(db)
    return await service.get_active_misconceptions(learner_id, concept_id=concept_id)


@router.patch("/{learner_id}/misconceptions/{misconception_id}", response_model=MisconceptionResponse)
async def update_misconception(
    learner_id: int,
    misconception_id: int,
    data: MisconceptionUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update or resolve a misconception."""
    service = MisconceptionService(db)

    if data.status and data.status.value == "resolved":
        res = await service.resolve_misconception(
            misconception_id, resolution_notes=data.resolution_notes
        )
    elif data.severity is not None:
        res = await service.update_severity(misconception_id, data.severity)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update fields specified",
        )

    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Misconception {misconception_id} not found",
        )
    return res


@router.get("/{learner_id}/gaps/{concept_id}", response_model=GapAnalysisResponse)
async def analyze_prerequisite_gaps(
    learner_id: int,
    concept_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Perform prerequisite gap analysis for target concept."""
    try:
        result = await find_learning_gaps(db, learner_id, concept_id)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        )

    return GapAnalysisResponse(
        target_concept_id=result.target_concept_id,
        target_concept_name=result.target_concept_name,
        prerequisites=[
            ConceptGapInfoResponse(
                concept_id=p.concept_id,
                concept_name=p.concept_name,
                effective_mastery=p.effective_mastery,
                classification=p.classification,
                mastery_probability=p.mastery_probability,
                forgetting_state=p.forgetting_state,
                confidence=p.confidence,
                depth=p.depth,
            )
            for p in result.prerequisites
        ],
        weak_prerequisites=[
            ConceptGapInfoResponse(
                concept_id=p.concept_id,
                concept_name=p.concept_name,
                effective_mastery=p.effective_mastery,
                classification=p.classification,
                mastery_probability=p.mastery_probability,
                forgetting_state=p.forgetting_state,
                confidence=p.confidence,
                depth=p.depth,
            )
            for p in result.weak_prerequisites
        ],
        prerequisite_edges=result.prerequisite_edges,
        has_gaps=result.has_gaps,
    )
