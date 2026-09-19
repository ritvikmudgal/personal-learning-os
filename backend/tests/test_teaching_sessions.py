"""Tests for TeachingSession persistence and management."""

import pytest
from app.db.repositories.session_repo import TeachingSessionRepository


@pytest.mark.asyncio
async def test_teaching_session_crud_and_message_appending(test_session, default_learner):
    """Test session creation, message appending, state updating, and listing."""
    repo = TeachingSessionRepository(test_session)

    session = await repo.create(
        learner_id=default_learner.id,
        user_goal="Teach me recursion",
        teaching_plan=["Step 1", "Step 2"],
    )

    assert session.id is not None
    assert session.status == "active"
    assert session.user_goal == "Teach me recursion"
    assert len(session.teaching_plan) == 2

    # Add messages
    await repo.add_message(session.id, sender="user", text="Teach me recursion")
    await repo.add_message(session.id, sender="ai", text="Recursion is when a function calls itself.")

    updated = await repo.get_by_id(session.id)
    assert len(updated.messages) == 2
    assert updated.messages[0]["sender"] == "user"
    assert updated.messages[1]["sender"] == "ai"

    # Get active session
    active = await repo.get_active_session(default_learner.id)
    assert active is not None
    assert active.id == session.id

    # Complete session
    await repo.update_state(session.id, status="completed")
    completed = await repo.get_by_id(session.id)
    assert completed.status == "completed"

    active_after = await repo.get_active_session(default_learner.id)
    assert active_after is None
