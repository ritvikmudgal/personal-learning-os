"""LangGraph stateful learning workflow orchestrator.

Creates an explicit, bounded state graph that orchestrates:
Goal Resolution -> Context Loading -> Prerequisite Gap Analysis -> RAG Retrieval ->
Teaching Plan -> Explanation Generation -> Learner Response Evaluation -> Evidence Candidate Persistence -> Routing.
"""

from typing import Any, Literal
from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.concept_repo import ConceptRepository
from app.domain.concept import ConceptCreate
from app.domain.evidence import EvidenceCreate, EvidenceType
from app.embeddings.factory import get_embedding_provider
from app.engine.context_builder import ContextBuilderService, BuiltContext
from app.engine.gap_analysis import find_learning_gaps
from app.engine.learning_state import LearningState
from app.engine.update_engine import update_state_from_evidence
from app.llm.factory import get_provider
from app.llm.tutor_operations import TutorLLMOperations
from app.services.evidence_service import EvidenceService
from app.services.graph_service import GraphService
from app.services.learner_state_service import LearnerStateService
from app.services.misconception_service import MisconceptionService
from app.services.retrieval_service import RetrievalService
from app.utils.logging import get_logger

logger = get_logger("engine.learning_graph")


class LearningGraphRunner:
    """Orchestrates the LangGraph learning workflow execution."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.provider = get_provider()
        self.tutor_ops = TutorLLMOperations(self.provider)
        self.graph_service = GraphService(session)
        self.concept_repo = ConceptRepository(session)
        self.state_service = LearnerStateService(session)
        self.evidence_service = EvidenceService(session)
        self.misconception_service = MisconceptionService(session)
        self.retrieval_service = RetrievalService(session, embedding_provider=get_embedding_provider())
        self.context_builder = ContextBuilderService(session)

    # --- Node Functions ---

    async def understand_goal(self, state: LearningState) -> LearningState:
        """Parse goal and resolve target concept against Concept Graph."""
        from app.utils.query_cleaner import clean_concept_name, strip_conversational_noise

        user_goal = state.get("user_goal", "")
        concepts = await self.graph_service.get_all_concepts()
        concepts_list = [{"id": c.id, "name": c.name} for c in concepts]

        # 1. Try deterministic Python-side concept resolution first (1ms)
        det_match = self.tutor_ops.deterministic_concept_resolution(user_goal, concepts_list)
        if det_match:
            matched_id = det_match["matched_id"]
            matched_name = det_match["matched_name"]
            intent = "teach"
        else:
            # Fall back to single LLM intent & concept resolution if no exact/substring match
            intent_res = await self.tutor_ops.classify_learning_intent(user_goal)
            raw_concept = intent_res.get("target_concept", user_goal)
            intent = intent_res.get("intent", "teach")

            res = await self.tutor_ops.resolve_concept_name(raw_concept, concepts_list)
            matched_id = res.get("matched_id")
            matched_name = clean_concept_name(res.get("matched_name")) or strip_conversational_noise(raw_concept) or "Learning Topic"

        # Check for explicit user intent override triggers
        lower_goal = user_goal.lower()
        override_triggers = [
            "skip", "already know", "don't want to study", "do not want to study",
            "move to", "move on to", "direct to", "continue with", "continue to"
        ]
        is_override = intent == "override" or any(trig in lower_goal for trig in override_triggers)
        state["override_prerequisites"] = is_override

        if matched_id is None:
            # Create a new concept in the graph dynamically
            try:
                new_concept = await self.concept_repo.create(
                    ConceptCreate(name=matched_name, description=f"Concept related to '{user_goal}'")
                )
                matched_id = new_concept.id
                matched_name = new_concept.name
            except Exception as e:
                logger.warning("Failed to auto-create concept '%s': %s", matched_name, e)

        state["target_concept_id"] = matched_id
        state["target_concept_name"] = matched_name
        state["current_concept_id"] = matched_id
        state["current_concept_name"] = matched_name
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    async def load_learner_context(self, state: LearningState) -> LearningState:
        """Load 6D learner states and active misconceptions for target concept."""
        learner_id = state.get("learner_id", 1)
        target_id = state.get("target_concept_id")

        snapshots = {}
        if target_id is not None:
            ks = await self.state_service.get_state(learner_id, target_id)
            if ks:
                snapshots[target_id] = {
                    "mastery_probability": ks.mastery_probability,
                    "knowledge_strength": ks.knowledge_strength,
                    "forgetting_state": ks.forgetting_state,
                    "confidence": ks.confidence,
                }

        misc_list = []
        if target_id is not None:
            active_m = await self.misconception_service.get_active_misconceptions(learner_id, target_id)
            misc_list = [{"id": m.id, "description": m.description, "severity": m.severity} for m in active_m]

        state["learner_state_snapshots"] = snapshots
        state["misconceptions"] = misc_list
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    async def analyze_prerequisites(self, state: LearningState) -> LearningState:
        """Perform gap analysis to find weak/unknown prerequisites."""
        learner_id = state.get("learner_id", 1)
        target_id = state.get("target_concept_id")

        weak_gaps = []
        known_prereqs = []

        if target_id is not None:
            try:
                gap_res = await find_learning_gaps(self.session, learner_id, target_id)
                for wp in gap_res.weak_prerequisites:
                    weak_gaps.append({
                        "id": wp.concept_id,
                        "name": wp.concept_name,
                        "mastery": wp.effective_mastery,
                        "classification": wp.classification,
                    })
                for sp in gap_res.prerequisites:
                    if sp.classification == "strong":
                        known_prereqs.append({
                            "id": sp.concept_id,
                            "name": sp.concept_name,
                            "mastery": sp.effective_mastery,
                        })
            except Exception as e:
                logger.warning("Prerequisite analysis error: %s", e)

        state["prerequisite_gaps"] = weak_gaps
        state["relevant_known_concepts"] = known_prereqs

        # Respect user intent override: do not force gap teaching if user asked to bypass/target directly
        if weak_gaps and not state.get("override_prerequisites"):
            first_gap = weak_gaps[0]
            state["current_concept_id"] = first_gap["id"]
            state["current_concept_name"] = first_gap["name"]
            state["next_action"] = "teach_gap"
        else:
            state["current_concept_id"] = target_id
            state["current_concept_name"] = state.get("target_concept_name")
            state["next_action"] = "teach_target"

        state["step_count"] = state.get("step_count", 0) + 1
        return state

    async def retrieve_materials(self, state: LearningState) -> LearningState:
        """Retrieve relevant Library materials using semantic vector search (Layer 3 RAG)."""
        from app.utils.query_cleaner import build_clean_search_query

        learner_id = state.get("learner_id", 1)
        target_name = state.get("current_concept_name") or state.get("target_concept_name", "")
        user_goal = state.get("user_goal", "")

        materials = []
        try:
            search_query = build_clean_search_query(target_name, user_goal)
            res_list = await self.retrieval_service.search_semantic(
                query=search_query,
                learner_id=learner_id,
                top_k=3,
            )
            if res_list:
                for r in res_list:
                    materials.append({
                        "chunk_id": r.chunk_id,
                        "material_title": r.material_title,
                        "content": r.clean_content[:300],
                        "page_number": r.page_number,
                        "section_header": r.section_header,
                    })
        except Exception as e:
            logger.warning("Material retrieval error in graph: %s", e)

        state["retrieved_material"] = materials
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    async def plan_teaching(self, state: LearningState) -> LearningState:
        """Synthesize personalized step-by-step teaching plan deterministically for low latency."""
        target_name = state.get("target_concept_name", "the requested topic")
        weak_names = [g["name"] for g in state.get("prerequisite_gaps", [])]

        if weak_names:
            plan = [
                f"Review foundation: {', '.join(weak_names[:2])}",
                f"Introduce core ideas of {target_name}",
                f"Explore key mechanisms and examples",
                f"Verify understanding of {target_name}",
            ]
        else:
            plan = [
                f"Introduce core concept: {target_name}",
                f"Explore key mechanisms and examples",
                f"Verify understanding of {target_name}",
            ]

        state["teaching_plan"] = plan
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    async def execute_context_pipeline_parallel(self, state: LearningState) -> LearningState:
        """Execute independent context loading, gap analysis, and material retrieval concurrently."""
        import asyncio
        state = await self.understand_goal(state)

        # Execute load_learner_context, analyze_prerequisites, and retrieve_materials concurrently
        await asyncio.gather(
            self.load_learner_context(state),
            self.analyze_prerequisites(state),
            self.retrieve_materials(state),
        )

        state = await self.plan_teaching(state)
        return state

    async def teach_step(self, state: LearningState) -> LearningState:
        """Generate tailored explanation turn using budgeted context."""
        learner_id = state.get("learner_id", 1)
        concept_id = state.get("current_concept_id")
        concept_name = state.get("current_concept_name") or state.get("target_concept_name", "Concept")
        user_goal = state.get("user_goal", "")
        history = state.get("conversation_context", [])

        # Build token-budgeted prompt context
        built_ctx: BuiltContext = await self.context_builder.build_tutor_context(
            learner_id=learner_id,
            target_concept_id=concept_id,
            target_concept_name=concept_name,
            user_message=user_goal,
            recent_history=history,
        )

        strategy = "gap_fix" if state.get("next_action") == "teach_gap" else "direct"
        explanation = await self.tutor_ops.generate_explanation(
            formatted_context=built_ctx.formatted_context_str,
            strategy=strategy,
        )

        state["explanation_output"] = explanation
        state["provenance"] = [
            {"type": p.source_type, "title": p.title, "detail": p.detail}
            for p in built_ctx.provenance_list
        ]
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    async def evaluate_response(self, state: LearningState) -> LearningState:
        """Evaluate learner response turn and generate structured evidence candidates."""
        latest_res = state.get("latest_response", "")
        current_name = state.get("current_concept_name", "")

        if not latest_res:
            return state

        eval_res = await self.tutor_ops.evaluate_learner_response(
            learner_response=latest_res,
            current_concept=current_name,
            expected_context=state.get("explanation_output", "")[:500],
        )

        candidates = list(state.get("evidence_candidates", []))
        cand = {
            "concept_id": state.get("current_concept_id"),
            "concept_name": current_name,
            "quality": eval_res["result_quality"],
            "is_sufficient": eval_res["is_sufficient"],
            "misconception_detected": eval_res.get("misconception_detected"),
            "feedback": eval_res.get("feedback"),
        }
        candidates.append(cand)
        state["evidence_candidates"] = candidates
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    async def update_learner_state(self, state: LearningState) -> LearningState:
        """Route evidence candidates to Layer 2 Evidence Service -> Update Engine.
        
        CRITICAL ISOLATION RULE: The LLM NEVER directly overwrites KnowledgeState values.
        Evidence candidates pass through existing Layer 2 update logic.
        """
        learner_id = state.get("learner_id", 1)
        candidates = state.get("evidence_candidates", [])

        for cand in candidates:
            cid = cand.get("concept_id")
            if cid is None:
                continue

            quality = float(cand.get("quality", 0.7))
            try:
                # 1. Add evidence record & update state via EvidenceService
                await self.evidence_service.record_evidence(
                    learner_id=learner_id,
                    concept_id=cid,
                    evidence_type=EvidenceType.EXPLANATION,
                    result_quality=quality,
                    source="AI Tutor Study Session",
                    notes=cand.get("feedback"),
                )

                # 2. Track misconception if detected
                misc_desc = cand.get("misconception_detected")
                if misc_desc:
                    await self.misconception_service.record_misconception(
                        learner_id=learner_id,
                        description=misc_desc,
                        concept_id=cid,
                        severity=0.6,
                    )
            except Exception as e:
                logger.warning("Error persisting evidence candidate for concept %s: %s", cid, e)

        state["step_count"] = state.get("step_count", 0) + 1
        return state

    async def route_next(self, state: LearningState) -> LearningState:
        """Determine next workflow action."""
        candidates = state.get("evidence_candidates", [])

        if candidates:
            latest = candidates[-1]
            if not latest.get("is_sufficient", True):
                state["next_action"] = "backtrack"
            else:
                # If gap was being taught and is now sufficient, advance to target concept
                if state.get("next_action") == "teach_gap":
                    state["current_concept_id"] = state.get("target_concept_id")
                    state["current_concept_name"] = state.get("target_concept_name")
                    state["next_action"] = "teach_target"
                else:
                    state["next_action"] = "advance"

        state["step_count"] = state.get("step_count", 0) + 1
        return state


def build_learning_graph(runner: LearningGraphRunner):
    """Construct compiled LangGraph StateGraph."""
    graph = StateGraph(LearningState)

    graph.add_node("understand_goal", runner.understand_goal)
    graph.add_node("load_learner_context", runner.load_learner_context)
    graph.add_node("analyze_prerequisites", runner.analyze_prerequisites)
    graph.add_node("retrieve_materials", runner.retrieve_materials)
    graph.add_node("plan_teaching", runner.plan_teaching)
    graph.add_node("teach_step", runner.teach_step)
    graph.add_node("evaluate_response", runner.evaluate_response)
    graph.add_node("update_learner_state", runner.update_learner_state)
    graph.add_node("route_next", runner.route_next)

    # Entry point
    graph.set_entry_point("understand_goal")

    # Sequence edges
    graph.add_edge("understand_goal", "load_learner_context")
    graph.add_edge("load_learner_context", "analyze_prerequisites")
    graph.add_edge("analyze_prerequisites", "retrieve_materials")
    graph.add_edge("retrieve_materials", "plan_teaching")
    graph.add_edge("plan_teaching", "teach_step")
    graph.add_edge("teach_step", "evaluate_response")
    graph.add_edge("evaluate_response", "update_learner_state")
    graph.add_edge("update_learner_state", "route_next")
    graph.add_edge("route_next", END)

    return graph.compile()
