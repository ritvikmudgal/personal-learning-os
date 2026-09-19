"""Misconception service — tracking and managing learner misconceptions."""

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import KnowledgeState, Misconception, MisconceptionStatus
from app.db.repositories.knowledge_state_repo import KnowledgeStateRepository
from app.utils.logging import get_logger

logger = get_logger("service.misconception")


class MisconceptionService:
    """Service for creating, tracking, and resolving learner misconceptions."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.state_repo = KnowledgeStateRepository(session)

    async def record_misconception(
        self,
        learner_id: int,
        description: str,
        concept_id: int | None = None,
        severity: float = 0.5,
    ) -> Misconception:
        """Record a new misconception or observe an existing active matching misconception."""
        # Check if an active misconception with same description exists
        query = select(Misconception).where(
            Misconception.learner_id == learner_id,
            Misconception.description == description,
            Misconception.status != MisconceptionStatus.RESOLVED,
        )
        if concept_id is not None:
            query = query.where(Misconception.concept_id == concept_id)

        result = await self.session.execute(query)
        existing = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if existing:
            existing.evidence_count += 1
            existing.last_observed_at = now
            existing.severity = max(existing.severity, severity)
            await self.session.flush()
            await self.session.refresh(existing)
            logger.info("Observed existing misconception: id=%d", existing.id)
            misconception = existing
        else:
            misconception = Misconception(
                learner_id=learner_id,
                concept_id=concept_id,
                description=description,
                severity=severity,
                status=MisconceptionStatus.ACTIVE,
                detected_at=now,
                last_observed_at=now,
                evidence_count=1,
                resolved=False,
            )
            self.session.add(misconception)
            await self.session.flush()
            await self.session.refresh(misconception)
            logger.info("Created new misconception: id=%d", misconception.id)

        if concept_id is not None:
            await self.recalculate_concept_misconception_severity(learner_id, concept_id)

        return misconception

    async def get_active_misconceptions(
        self, learner_id: int, concept_id: int | None = None
    ) -> list[Misconception]:
        """Get active misconceptions for a learner, optionally filtered by concept."""
        query = select(Misconception).where(
            Misconception.learner_id == learner_id,
            Misconception.status != MisconceptionStatus.RESOLVED,
        )
        if concept_id is not None:
            query = query.where(Misconception.concept_id == concept_id)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def resolve_misconception(
        self, misconception_id: int, resolution_notes: str | None = None
    ) -> Misconception | None:
        """Mark a misconception as resolved."""
        result = await self.session.execute(
            select(Misconception).where(Misconception.id == misconception_id)
        )
        misconception = result.scalar_one_or_none()
        if not misconception:
            return None

        now = datetime.now(timezone.utc)
        misconception.status = MisconceptionStatus.RESOLVED
        misconception.resolved = True
        misconception.resolved_at = now
        misconception.resolution_notes = resolution_notes
        await self.session.flush()
        await self.session.refresh(misconception)

        if misconception.concept_id is not None:
            await self.recalculate_concept_misconception_severity(
                misconception.learner_id, misconception.concept_id
            )

        logger.info("Resolved misconception: id=%d", misconception_id)
        return misconception

    async def update_severity(
        self, misconception_id: int, severity: float
    ) -> Misconception | None:
        """Update severity of a misconception."""
        result = await self.session.execute(
            select(Misconception).where(Misconception.id == misconception_id)
        )
        misconception = result.scalar_one_or_none()
        if not misconception:
            return None

        misconception.severity = min(max(severity, 0.0), 1.0)
        await self.session.flush()
        await self.session.refresh(misconception)

        if misconception.concept_id is not None:
            await self.recalculate_concept_misconception_severity(
                misconception.learner_id, misconception.concept_id
            )

        return misconception

    async def recalculate_concept_misconception_severity(
        self, learner_id: int, concept_id: int
    ) -> float:
        """Recalculate max active misconception severity and update KnowledgeState."""
        active = await self.get_active_misconceptions(learner_id, concept_id)
        max_severity = max([m.severity for m in active], default=0.0)

        state = await self.state_repo.get_or_create(learner_id, concept_id)
        state.misconception_severity = max_severity
        await self.state_repo.update(state)

        return max_severity
