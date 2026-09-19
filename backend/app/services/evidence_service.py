"""Evidence service — recording evidence and triggering state updates."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Evidence, EvidenceType, KnowledgeState
from app.db.repositories.evidence_repo import EvidenceRepository
from app.db.repositories.knowledge_state_repo import KnowledgeStateRepository
from app.engine.update_engine import update_state_from_evidence
from app.utils.logging import get_logger

logger = get_logger("service.evidence")


class EvidenceService:
    """Service for recording learning evidence and updating learner state."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.evidence_repo = EvidenceRepository(session)
        self.state_repo = KnowledgeStateRepository(session)

    async def record_evidence(
        self,
        learner_id: int,
        concept_id: int | None,
        evidence_type: EvidenceType | str,
        result_quality: float,
        difficulty: float | None = None,
        confidence: float | None = None,
        source: str = "user_interaction",
        misconception_info: dict | None = None,
        notes: str | None = None,
    ) -> tuple[Evidence, KnowledgeState | None]:
        """Record a piece of evidence and update learner state if concept_id is provided."""
        if isinstance(evidence_type, str):
            evidence_type = EvidenceType(evidence_type)

        evidence = Evidence(
            learner_id=learner_id,
            concept_id=concept_id,
            evidence_type=evidence_type,
            result_quality=result_quality,
            difficulty=difficulty,
            confidence=confidence,
            source=source,
            misconception_info=misconception_info,
            notes=notes,
        )

        saved_evidence = await self.evidence_repo.create(evidence)

        updated_state = None
        if concept_id is not None:
            state = await self.state_repo.get_or_create(learner_id, concept_id)
            updated_state = update_state_from_evidence(state, saved_evidence)
            await self.state_repo.update(updated_state)
            logger.info(
                "Updated learner state for concept %d: mastery=%.2f, strength=%.2f",
                concept_id,
                updated_state.mastery_probability,
                updated_state.knowledge_strength,
            )

        return saved_evidence, updated_state

    async def get_evidence_for_concept(
        self, learner_id: int, concept_id: int
    ) -> list[Evidence]:
        """Get all evidence records for a learner-concept pair."""
        return await self.evidence_repo.get_for_learner_concept(learner_id, concept_id)

    async def get_recent_evidence(
        self, learner_id: int, concept_id: int, limit: int = 10
    ) -> list[Evidence]:
        """Get recent evidence records for a learner-concept pair."""
        return await self.evidence_repo.get_recent(learner_id, concept_id, limit=limit)
