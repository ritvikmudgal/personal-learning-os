"""Tutor service — main orchestrator service for personalized learning sessions."""

from typing import Any, AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.session_repo import TeachingSessionRepository
from app.db.repositories.learner_repo import LearnerRepository
from app.engine.learning_graph import LearningGraphRunner, build_learning_graph
from app.engine.learning_state import LearningState
from app.utils.logging import get_logger

logger = get_logger("service.tutor")


class TutorService:
    """Service handling interactive tutor sessions and LangGraph execution."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.session_repo = TeachingSessionRepository(session)
        self.learner_repo = LearnerRepository(session)
        self.graph_runner = LearningGraphRunner(session)
        self.compiled_graph = build_learning_graph(self.graph_runner)

    async def handle_user_message(
        self,
        user_message: str,
        learner_id: int | None = None,
        session_id: int | None = None,
    ) -> dict[str, Any]:
        """Process user message through LangGraph state machine and persist session."""
        if learner_id is None:
            learner = await self.learner_repo.get_or_create_default()
            learner_id = learner.id

        # 1. Fetch or create active session
        active_session = None
        if session_id is not None:
            active_session = await self.session_repo.get_by_id(session_id)

        if not active_session:
            active_session = await self.session_repo.get_active_session(learner_id)

        if not active_session:
            active_session = await self.session_repo.create(
                learner_id=learner_id,
                user_goal=user_message,
            )

        # 2. Append user message to session
        await self.session_repo.add_message(active_session.id, sender="user", text=user_message)

        # 3. Construct initial LangGraph input state
        history = active_session.messages or []
        init_state: LearningState = {
            "learner_id": learner_id,
            "user_goal": user_message,
            "target_concept_id": active_session.target_concept_id,
            "target_concept_name": None,
            "current_concept_id": active_session.target_concept_id,
            "current_concept_name": None,
            "prerequisite_gaps": [],
            "relevant_known_concepts": [],
            "learner_state_snapshots": {},
            "misconceptions": [],
            "retrieved_material": [],
            "teaching_plan": active_session.teaching_plan or [],
            "conversation_context": history,
            "evidence_candidates": [],
            "next_action": "teach_target",
            "session_id": active_session.id,
            "latest_response": user_message,
            "explanation_output": "",
            "provenance": [],
            "step_count": 0,
        }

        # 4. Invoke LangGraph
        final_state: LearningState = await self.compiled_graph.ainvoke(init_state)

        # 5. Extract results
        explanation = final_state.get("explanation_output", "I'm here to help you learn!")
        provenance = final_state.get("provenance", [])
        teaching_plan = final_state.get("teaching_plan", [])
        target_concept_id = final_state.get("target_concept_id")
        target_concept_name = final_state.get("target_concept_name")

        meta = {
            "provenance": provenance,
            "prerequisite_gaps": final_state.get("prerequisite_gaps", []),
            "target_concept_id": target_concept_id,
            "target_concept_name": target_concept_name,
            "next_action": final_state.get("next_action"),
        }

        # 6. Update session record
        visited = list(active_session.concepts_visited or [])
        if target_concept_id and target_concept_id not in visited:
            visited.append(target_concept_id)

        await self.session_repo.add_message(
            session_id=active_session.id,
            sender="ai",
            text=explanation,
            metadata=meta,
        )

        await self.session_repo.update_state(
            session_id=active_session.id,
            concepts_visited=visited,
            teaching_plan=teaching_plan,
            session_metadata=meta,
        )

        return {
            "session_id": active_session.id,
            "text": explanation,
            "target_concept_id": target_concept_id,
            "target_concept_name": target_concept_name,
            "teaching_plan": teaching_plan,
            "provenance": provenance,
            "prerequisite_gaps": final_state.get("prerequisite_gaps", []),
            "next_action": final_state.get("next_action"),
        }

    async def clear_session(self, session_id: int) -> bool:
        """Mark session completed."""
        res = await self.session_repo.update_state(session_id=session_id, status="completed")
        return res is not None
