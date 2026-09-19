"""Learner state service — managing learner knowledge states per concept."""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import KnowledgeState
from app.db.repositories.knowledge_state_repo import KnowledgeStateRepository
from app.engine.decay_service import compute_decay
from app.utils.logging import get_logger

logger = get_logger("service.learner_state")


class LearnerStateService:
    """Service for retrieving and managing multi-dimensional learner states."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = KnowledgeStateRepository(session)

    async def get_state(
        self, learner_id: int, concept_id: int
    ) -> KnowledgeState | None:
        """Get knowledge state for learner-concept pair."""
        return await self.repo.get_by_learner_concept(learner_id, concept_id)

    async def get_or_create_state(
        self, learner_id: int, concept_id: int
    ) -> KnowledgeState:
        """Get existing state or create a new default knowledge state."""
        return await self.repo.get_or_create(learner_id, concept_id)

    async def get_all_states(
        self, learner_id: int
    ) -> list[KnowledgeState]:
        """Get all knowledge states for a learner."""
        return await self.repo.get_all_for_learner(learner_id)

    async def get_current_state(
        self, learner_id: int, concept_id: int, now: datetime | None = None
    ) -> KnowledgeState | None:
        """Get knowledge state with current forgetting_state calculated based on decay."""
        state = await self.get_state(learner_id, concept_id)
        if state is None:
            return None

        if now is None:
            now = datetime.now(timezone.utc)

        # Compute updated forgetting state
        decay_val = compute_decay(state, now)
        state.forgetting_state = decay_val
        return state
