"""Evidence repository — database operations for learning evidence records."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Evidence
from app.utils.logging import get_logger

logger = get_logger("repo.evidence")


class EvidenceRepository:
    """Repository for Evidence CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, evidence: Evidence) -> Evidence:
        """Persist a new evidence record."""
        self.session.add(evidence)
        await self.session.flush()
        await self.session.refresh(evidence)
        logger.info(
            "Created evidence: id=%d learner=%d concept=%s type=%s",
            evidence.id, evidence.learner_id,
            evidence.concept_id, evidence.evidence_type.value,
        )
        return evidence

    async def get_by_id(self, evidence_id: int) -> Evidence | None:
        """Get an evidence record by ID."""
        result = await self.session.execute(
            select(Evidence).where(Evidence.id == evidence_id)
        )
        return result.scalar_one_or_none()

    async def get_for_learner_concept(
        self, learner_id: int, concept_id: int
    ) -> list[Evidence]:
        """Get all evidence for a specific learner-concept pair, ordered by time."""
        result = await self.session.execute(
            select(Evidence)
            .where(
                Evidence.learner_id == learner_id,
                Evidence.concept_id == concept_id,
            )
            .order_by(Evidence.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_recent(
        self, learner_id: int, concept_id: int, limit: int = 10
    ) -> list[Evidence]:
        """Get the N most recent evidence records for a learner-concept pair."""
        result = await self.session.execute(
            select(Evidence)
            .where(
                Evidence.learner_id == learner_id,
                Evidence.concept_id == concept_id,
            )
            .order_by(Evidence.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_all_for_learner(self, learner_id: int) -> list[Evidence]:
        """Get all evidence records for a learner."""
        result = await self.session.execute(
            select(Evidence)
            .where(Evidence.learner_id == learner_id)
            .order_by(Evidence.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_for_learner_concept(
        self, learner_id: int, concept_id: int
    ) -> int:
        """Count evidence records for a learner-concept pair."""
        result = await self.session.execute(
            select(Evidence)
            .where(
                Evidence.learner_id == learner_id,
                Evidence.concept_id == concept_id,
            )
        )
        return len(list(result.scalars().all()))
