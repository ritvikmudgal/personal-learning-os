"""Learner profile repository — database operations for learner data."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import KnowledgeState, LearnerProfile
from app.domain.learner import LearnerCreate, LearnerUpdate
from app.utils.logging import get_logger

logger = get_logger("repo.learner")


class LearnerRepository:
    """Repository for learner profile CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: LearnerCreate) -> LearnerProfile:
        """Create a new learner profile."""
        learner = LearnerProfile(
            name=data.name,
            email=data.email,
            preferences=data.preferences or {},
        )
        self.session.add(learner)
        await self.session.flush()
        await self.session.refresh(learner)
        logger.info("Created learner profile: id=%d name=%s", learner.id, learner.name)
        return learner

    async def get_by_id(self, learner_id: int) -> LearnerProfile | None:
        """Get a learner profile by ID."""
        result = await self.session.execute(
            select(LearnerProfile).where(LearnerProfile.id == learner_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[LearnerProfile]:
        """Get all learner profiles."""
        result = await self.session.execute(select(LearnerProfile))
        return list(result.scalars().all())

    async def update(
        self, learner_id: int, data: LearnerUpdate
    ) -> LearnerProfile | None:
        """Update a learner profile. Returns None if not found."""
        learner = await self.get_by_id(learner_id)
        if learner is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(learner, field, value)

        await self.session.flush()
        await self.session.refresh(learner)
        logger.info("Updated learner profile: id=%d", learner_id)
        return learner

    async def delete(self, learner_id: int) -> bool:
        """Delete a learner profile. Returns True if deleted."""
        learner = await self.get_by_id(learner_id)
        if learner is None:
            return False

        await self.session.delete(learner)
        await self.session.flush()
        logger.info("Deleted learner profile: id=%d", learner_id)
        return True

    async def get_knowledge_states(
        self, learner_id: int
    ) -> list[KnowledgeState]:
        """Get all knowledge states for a learner, with concept info loaded."""
        result = await self.session.execute(
            select(KnowledgeState)
            .where(KnowledgeState.learner_id == learner_id)
            .options(selectinload(KnowledgeState.concept))
        )
        return list(result.scalars().all())
