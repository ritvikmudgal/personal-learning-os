"""FastAPI router for AI Learning Engine & Personalized Tutor."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.repositories.learner_repo import LearnerRepository
from app.services.tutor_service import TutorService
from app.db.repositories.session_repo import TeachingSessionRepository

tutor_router = APIRouter(prefix="/tutor", tags=["Tutor"])


# --- Schemas ---

class TutorChatRequest(BaseModel):
    user_message: str = Field(..., description="User prompt or concept learning goal")
    session_id: int | None = Field(None, description="Optional active session ID")


class ProvenanceItemSchema(BaseModel):
    type: str
    title: str
    detail: str


class TutorChatResponse(BaseModel):
    session_id: int
    text: str
    target_concept_id: int | None = None
    target_concept_name: str | None = None
    teaching_plan: list[str] = Field(default_factory=list)
    provenance: list[ProvenanceItemSchema] = Field(default_factory=list)
    prerequisite_gaps: list[dict] = Field(default_factory=list)
    next_action: str | None = None


# --- Endpoints ---

@tutor_router.post("/chat", response_model=TutorChatResponse)
async def chat_with_tutor(
    req: TutorChatRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Interact with the personalized AI tutor via LangGraph learning engine."""
    learner_repo = LearnerRepository(db)
    learner = await learner_repo.get_or_create_default()
    service = TutorService(db)

    try:
        result = await service.handle_user_message(
            user_message=req.user_message,
            learner_id=learner.id,
            session_id=req.session_id,
        )
        return TutorChatResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tutor engine error: {str(e)}",
        )


@tutor_router.get("/session/active")
async def get_active_session(
    db: AsyncSession = Depends(get_db_session),
):
    """Get the active teaching session for the current learner."""
    learner_repo = LearnerRepository(db)
    learner = await learner_repo.get_or_create_default()
    repo = TeachingSessionRepository(db)
    session = await repo.get_active_session(learner.id)
    if not session:
        return {"active": False, "session": None}

    return {
        "active": True,
        "session": {
            "id": session.id,
            "user_goal": session.user_goal,
            "target_concept_id": session.target_concept_id,
            "teaching_plan": session.teaching_plan or [],
            "messages": session.messages or [],
            "session_metadata": session.session_metadata or {},
        },
    }


@tutor_router.post("/session/{session_id}/clear")
async def clear_session(
    session_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Clear/complete an active session."""
    service = TutorService(db)
    success = await service.clear_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    return {"status": "completed", "session_id": session_id}


@tutor_router.get("/sessions")
async def list_recent_sessions(
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session),
):
    """List recent teaching sessions."""
    learner_repo = LearnerRepository(db)
    learner = await learner_repo.get_or_create_default()
    repo = TeachingSessionRepository(db)
    sessions = await repo.get_recent_sessions(learner.id, limit=limit)
    return [
        {
            "id": s.id,
            "user_goal": s.user_goal,
            "target_concept_id": s.target_concept_id,
            "status": s.status,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "message_count": len(s.messages or []),
        }
        for s in sessions
    ]
