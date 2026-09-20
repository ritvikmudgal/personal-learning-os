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
        from app.utils.logging import get_logger
        logger = get_logger("api.tutor")
        logger.error("Unexpected error in tutor chat handler: %s", e, exc_info=True)
        return TutorChatResponse(
            session_id=req.session_id or 1,
            text="I encountered a temporary issue processing your request, but I'm here to help. Could you rephrase your learning request?",
            next_action="teach_target",
        )


@tutor_router.post("/chat/stream")
async def chat_with_tutor_stream(
    req: TutorChatRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Stream interactive tutor response tokens via Server-Sent Events (SSE).

    For NORMAL_CONVERSATION messages (greetings, thanks, capabilities),
    returns an instant JSON response with 0 LLM calls.
    For study/learning requests, streams SSE tokens from the tutor pipeline.
    """
    import json
    import time
    from fastapi.responses import JSONResponse, StreamingResponse
    from app.engine.ai_router import AIRouter, QueryCategory
    from app.utils.logging import get_logger

    logger = get_logger("api.tutor.stream")
    start_time = time.monotonic()

    # --- Fast deterministic pre-classification (no LLM, no embeddings) ---
    router = AIRouter(db)
    category = router.classify_request(req.user_message)

    if category == QueryCategory.NORMAL_CONVERSATION:
        # Instant deterministic response — no SSE, no DB session race, no LLM
        det_res = router._build_normal_conversation_response(req.user_message)
        elapsed_ms = (time.monotonic() - start_time) * 1000

        # Persist to session in the safe dependency-managed DB session
        learner_repo = LearnerRepository(db)
        learner = await learner_repo.get_or_create_default()
        session_repo = TeachingSessionRepository(db)

        active_session = None
        if req.session_id is not None:
            active_session = await session_repo.get_by_id(req.session_id)
        if not active_session:
            active_session = await session_repo.get_active_session(learner.id)
        if not active_session:
            active_session = await session_repo.create(
                learner_id=learner.id, user_goal=req.user_message,
            )

        await session_repo.add_message(active_session.id, sender="user", text=req.user_message)
        await session_repo.add_message(active_session.id, sender="ai", text=det_res["text"])

        logger.info(
            "[CHAT] message=%r route=DETERMINISTIC llm_calls=0 duration=%.0fms status=success",
            req.user_message, elapsed_ms,
        )

        # Return SSE-compatible payload as JSON so the frontend can handle it uniformly
        return JSONResponse(content={
            "type": "instant",
            "session_id": active_session.id,
            "text": det_res["text"],
            "target_concept_name": det_res.get("target_concept_name"),
            "teaching_plan": det_res.get("teaching_plan", []),
            "provenance": det_res.get("provenance", []),
        })

    # --- Streaming path for study/learning requests ---
    # Resolve learner in the dependency-managed session
    learner_repo = LearnerRepository(db)
    learner = await learner_repo.get_or_create_default()
    learner_id = learner.id

    async def event_generator():
        """SSE generator that manages its own DB session to avoid premature cleanup."""
        from app.db.database import get_session_factory
        import asyncio

        factory = get_session_factory()
        gen_logger = get_logger("api.tutor.stream.gen")
        gen_start = time.monotonic()

        async with factory() as gen_session:
            try:
                service = TutorService(gen_session)
                async for item in service.stream_user_message(
                    user_message=req.user_message,
                    learner_id=learner_id,
                    session_id=req.session_id,
                ):
                    event_name = item.get("event", "message")
                    data_json = json.dumps(item.get("data", {}))
                    yield f"event: {event_name}\ndata: {data_json}\n\n"

                elapsed_ms = (time.monotonic() - gen_start) * 1000
                gen_logger.info(
                    "[CHAT] message=%r route=STUDY llm_calls=1 duration=%.0fms status=success",
                    req.user_message, elapsed_ms,
                )
                await gen_session.commit()

            except asyncio.TimeoutError:
                elapsed_ms = (time.monotonic() - gen_start) * 1000
                gen_logger.error(
                    "[CHAT] message=%r route=STUDY duration=%.0fms status=timeout",
                    req.user_message, elapsed_ms,
                )
                fallback = json.dumps("I'm having trouble with the AI right now. You can still ask me about your study materials or concepts.")
                yield f"event: token\ndata: {fallback}\n\n"
                done = json.dumps({"session_id": req.session_id, "text": ""})
                yield f"event: done\ndata: {done}\n\n"
                await gen_session.rollback()

            except Exception as e:
                elapsed_ms = (time.monotonic() - gen_start) * 1000
                gen_logger.error(
                    "[CHAT] message=%r route=STUDY duration=%.0fms status=error error=%s",
                    req.user_message, elapsed_ms, str(e), exc_info=True,
                )
                fallback = json.dumps("I'm having trouble with the AI right now. You can still ask me about your study materials or concepts.")
                yield f"event: token\ndata: {fallback}\n\n"
                done = json.dumps({"session_id": req.session_id, "text": ""})
                yield f"event: done\ndata: {done}\n\n"
                await gen_session.rollback()

    return StreamingResponse(event_generator(), media_type="text/event-stream")





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
