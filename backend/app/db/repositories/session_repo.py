"""Teaching session repository — database operations for persistent learning sessions."""

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TeachingSession
from app.utils.logging import get_logger

logger = get_logger("repo.session")


class TeachingSessionRepository:
    """Repository for managing TeachingSession records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        learner_id: int,
        user_goal: str,
        target_concept_id: int | None = None,
        teaching_plan: list[str] | None = None,
        session_metadata: dict | None = None,
    ) -> TeachingSession:
        """Create a new teaching session."""
        ts = TeachingSession(
            learner_id=learner_id,
            target_concept_id=target_concept_id,
            user_goal=user_goal,
            status="active",
            started_at=datetime.now(timezone.utc),
            concepts_visited=[target_concept_id] if target_concept_id else [],
            teaching_plan=teaching_plan or [],
            messages=[],
            session_metadata=session_metadata or {},
        )
        self.session.add(ts)
        await self.session.flush()
        await self.session.refresh(ts)
        logger.info("Created teaching session: id=%d learner_id=%d goal='%s'", ts.id, learner_id, user_goal)
        return ts

    async def get_by_id(self, session_id: int) -> TeachingSession | None:
        """Get a teaching session by ID."""
        result = await self.session.execute(
            select(TeachingSession).where(TeachingSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_active_session(self, learner_id: int) -> TeachingSession | None:
        """Get the current active session for a learner if one exists."""
        result = await self.session.execute(
            select(TeachingSession)
            .where(
                TeachingSession.learner_id == learner_id,
                TeachingSession.status == "active",
            )
            .order_by(TeachingSession.updated_at.desc())
        )
        return result.scalars().first()

    async def get_recent_sessions(self, learner_id: int, limit: int = 10) -> list[TeachingSession]:
        """Get recent sessions for a learner."""
        result = await self.session.execute(
            select(TeachingSession)
            .where(TeachingSession.learner_id == learner_id)
            .order_by(TeachingSession.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def add_message(
        self,
        session_id: int,
        sender: str,
        text: str,
        metadata: dict | None = None,
    ) -> TeachingSession | None:
        """Append a message turn to the session."""
        ts = await self.get_by_id(session_id)
        if not ts:
            return None

        msgs = list(ts.messages or [])
        msg_entry = {
            "sender": sender,
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if metadata:
            msg_entry["metadata"] = metadata
        msgs.append(msg_entry)

        ts.messages = msgs
        ts.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(ts)
        return ts

    async def update_state(
        self,
        session_id: int,
        concepts_visited: list[int] | None = None,
        teaching_plan: list[str] | None = None,
        session_metadata: dict | None = None,
        status: str | None = None,
    ) -> TeachingSession | None:
        """Update session progress metadata."""
        ts = await self.get_by_id(session_id)
        if not ts:
            return None

        if concepts_visited is not None:
            ts.concepts_visited = concepts_visited
        if teaching_plan is not None:
            ts.teaching_plan = teaching_plan
        if session_metadata is not None:
            current_meta = dict(ts.session_metadata or {})
            current_meta.update(session_metadata)
            ts.session_metadata = current_meta
        if status is not None:
            ts.status = status
            if status in ("completed", "cleared"):
                ts.ended_at = datetime.now(timezone.utc)

        ts.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(ts)
        return ts
