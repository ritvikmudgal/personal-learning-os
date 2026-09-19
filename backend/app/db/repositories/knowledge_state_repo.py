"""Knowledge state repository — database operations for learner concept states."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import KnowledgeState
from app.utils.logging import get_logger

logger = get_logger("repo.knowledge_state")


class KnowledgeStateRepository:
    """Repository for KnowledgeState CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_learner_concept(
        self, learner_id: int, concept_id: int
    ) -> KnowledgeState | None:
        """Get a knowledge state for a specific learner-concept pair."""
        result = await self.session.execute(
            select(KnowledgeState)
            .where(
                KnowledgeState.learner_id == learner_id,
                KnowledgeState.concept_id == concept_id,
            )
            .options(selectinload(KnowledgeState.concept))
        )
        return result.scalar_one_or_none()

    async def create(
        self, learner_id: int, concept_id: int
    ) -> KnowledgeState:
        """Create a new knowledge state with default values."""
        state = KnowledgeState(
            learner_id=learner_id,
            concept_id=concept_id,
        )
        self.session.add(state)
        await self.session.flush()
        await self.session.refresh(state)
        logger.info(
            "Created knowledge state: learner=%d concept=%d",
            learner_id, concept_id,
        )
        return state

    async def get_or_create(
        self, learner_id: int, concept_id: int
    ) -> KnowledgeState:
        """Get existing state or create a new one with defaults."""
        state = await self.get_by_learner_concept(learner_id, concept_id)
        if state is None:
            state = await self.create(learner_id, concept_id)
        return state

    async def update(self, state: KnowledgeState) -> KnowledgeState:
        """Flush changes to a knowledge state."""
        await self.session.flush()
        await self.session.refresh(state)
        return state

    async def get_all_for_learner(
        self, learner_id: int
    ) -> list[KnowledgeState]:
        """Get all knowledge states for a learner, with concept info loaded."""
        result = await self.session.execute(
            select(KnowledgeState)
            .where(KnowledgeState.learner_id == learner_id)
            .options(selectinload(KnowledgeState.concept))
        )
        return list(result.scalars().all())
