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

        # Check AI Router for zero-LLM deterministic / retrieval paths
        from app.engine.ai_router import AIRouter, QueryCategory
        router = AIRouter(self.session)
        category = router.classify_request(user_message)

        if category in (QueryCategory.NORMAL_CONVERSATION, QueryCategory.DETERMINISTIC, QueryCategory.RETRIEVAL):
            det_res = await router.execute_deterministic_route(category, user_message, learner_id)
            meta = {
                "provenance": det_res.get("provenance", []),
                "prerequisite_gaps": [],
                "target_concept_id": None,
                "target_concept_name": det_res.get("target_concept_name"),
                "next_action": "teach_target",
            }
            await self.session_repo.add_message(active_session.id, sender="ai", text=det_res["text"], metadata=meta)
            return {
                "session_id": active_session.id,
                "text": det_res["text"],
                "target_concept_id": None,
                "target_concept_name": det_res.get("target_concept_name"),
                "teaching_plan": det_res.get("teaching_plan", []),
                "provenance": det_res.get("provenance", []),
                "prerequisite_gaps": [],
                "next_action": "teach_target",
            }

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

        # 4. Invoke LangGraph with graceful exception fallback
        try:
            final_state: LearningState = await self.compiled_graph.ainvoke(init_state)
            explanation = final_state.get("explanation_output") or "I'm here to help you learn! What topic would you like to explore?"
            provenance = final_state.get("provenance", [])
            teaching_plan = final_state.get("teaching_plan", [])
            target_concept_id = final_state.get("target_concept_id")
            target_concept_name = final_state.get("target_concept_name")
            prereq_gaps = final_state.get("prerequisite_gaps", [])
            next_action = final_state.get("next_action")
        except Exception as e:
            logger.error("Error executing learning graph: %s", e, exc_info=True)
            explanation = (
                "I encountered a temporary issue processing that request, but I'm here to help you study. "
                "Could you tell me what specific concept or question you'd like to work on?"
            )
            provenance = []
            teaching_plan = []
            target_concept_id = None
            target_concept_name = None
            prereq_gaps = []
            next_action = "teach_target"
            final_state = init_state

        meta = {
            "provenance": provenance,
            "prerequisite_gaps": prereq_gaps,
            "target_concept_id": target_concept_id,
            "target_concept_name": target_concept_name,
            "next_action": next_action,
        }

        # 5. Update session record
        visited = list(active_session.concepts_visited or [])
        if target_concept_id and target_concept_id not in visited:
            visited.append(target_concept_id)

        try:
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
        except Exception as e:
            logger.warning("Error persisting session updates: %s", e)

        return {
            "session_id": active_session.id,
            "text": explanation,
            "target_concept_id": target_concept_id,
            "target_concept_name": target_concept_name,
            "teaching_plan": teaching_plan,
            "provenance": provenance,
            "prerequisite_gaps": prereq_gaps,
            "next_action": next_action,
        }

    async def stream_user_message(
        self,
        user_message: str,
        learner_id: int | None = None,
        session_id: int | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream response tokens as SSE events and log latency performance telemetry."""
        from app.engine.learning_state import LearningState
        from app.utils.telemetry import TutorRequestProfiler

        profiler = TutorRequestProfiler()

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

        await self.session_repo.add_message(active_session.id, sender="user", text=user_message)

        # 1. Check AI Router for zero-LLM deterministic / retrieval paths
        from app.engine.ai_router import AIRouter, QueryCategory
        router = AIRouter(self.session)
        category = router.classify_request(user_message)

        if category in (QueryCategory.NORMAL_CONVERSATION, QueryCategory.DETERMINISTIC, QueryCategory.RETRIEVAL):
            det_res = await router.execute_deterministic_route(category, user_message, learner_id)
            meta = {
                "session_id": active_session.id,
                "target_concept_name": det_res.get("target_concept_name"),
                "teaching_plan": det_res.get("teaching_plan", []),
                "provenance": det_res.get("provenance", []),
                "next_action": "teach_target",
            }
            yield {"event": "metadata", "data": meta}
            text = det_res.get("text", "")
            # Stream text in small chunks for consistent UI animation without touching LLM
            for i in range(0, len(text), 40):
                yield {"event": "token", "data": text[i:i+40]}

            await self.session_repo.add_message(active_session.id, sender="ai", text=text, metadata=meta)
            profiler.log_summary(llm_calls_count=0)
            yield {"event": "done", "data": {"session_id": active_session.id, "text": text}}
            return

        # 2. Context Construction Pipeline for LLM Reasoning
        profiler.start_stage("context_pipeline")
        history = active_session.messages or []
        state: LearningState = {
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

        # Parallelized fast context execution
        state = await self.graph_runner.execute_context_pipeline_parallel(state)
        profiler.end_stage("context_pipeline")

        # Emit metadata event immediately
        meta = {
            "session_id": active_session.id,
            "target_concept_id": state.get("target_concept_id"),
            "target_concept_name": state.get("target_concept_name"),
            "teaching_plan": state.get("teaching_plan", []),
            "provenance": state.get("provenance", []),
            "next_action": state.get("next_action"),
        }
        yield {"event": "metadata", "data": meta}

        # 3. Stream LLM tokens
        profiler.start_stage("llm_first_token")
        built_ctx = await self.graph_runner.context_builder.build_tutor_context(
            learner_id=learner_id,
            target_concept_id=state.get("current_concept_id"),
            target_concept_name=state.get("current_concept_name") or state.get("target_concept_name", "Concept"),
            user_message=user_message,
            recent_history=history,
        )

        strategy = "gap_fix" if state.get("next_action") == "teach_gap" else "direct"
        full_text_chunks = []
        first_token_received = False

        try:
            async for token in self.graph_runner.tutor_ops.stream_explanation(
                formatted_context=built_ctx.formatted_context_str,
                strategy=strategy,
            ):
                if not first_token_received:
                    profiler.end_stage("llm_first_token")
                    profiler.start_stage("llm_completion")
                    first_token_received = True

                full_text_chunks.append(token)
                yield {"event": "token", "data": token}

        except Exception as e:
            logger.error("Error streaming LLM output: %s", e, exc_info=True)
            fallback_err = " I encountered a temporary issue processing your request."
            full_text_chunks.append(fallback_err)
            yield {"event": "token", "data": fallback_err}

        if first_token_received:
            profiler.end_stage("llm_completion")
        else:
            profiler.end_stage("llm_first_token")

        full_explanation = "".join(full_text_chunks).strip()

        # 4. Async session persistence & evidence tracking
        profiler.start_stage("evidence_processing")
        try:
            visited = list(active_session.concepts_visited or [])
            if state.get("target_concept_id") and state.get("target_concept_id") not in visited:
                visited.append(state.get("target_concept_id"))

            await self.session_repo.add_message(
                session_id=active_session.id,
                sender="ai",
                text=full_explanation,
                metadata=meta,
            )
            await self.session_repo.update_state(
                session_id=active_session.id,
                concepts_visited=visited,
                teaching_plan=state.get("teaching_plan", []),
                session_metadata=meta,
            )
        except Exception as e:
            logger.warning("Error finalizing session persistence: %s", e)

        profiler.end_stage("evidence_processing")
        profiler.log_summary(llm_calls_count=1)

        yield {"event": "done", "data": {"session_id": active_session.id, "text": full_explanation}}

    async def clear_session(self, session_id: int) -> bool:
        """Mark session completed."""
        res = await self.session_repo.update_state(session_id=session_id, status="completed")
        return res is not None

