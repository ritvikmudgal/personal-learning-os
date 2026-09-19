"""Learning state schema — TypedDict state container for LangGraph orchestration."""

from typing import TypedDict, Optional, Any


class LearningState(TypedDict, total=False):
    """Explicit state container managed by LangGraph state transitions.

    Tracks learner state, target concept, gap analysis, RAG retrieval, teaching plan,
    conversation history, structured evidence candidates, and routing flags.
    """

    learner_id: int
    user_goal: str
    target_concept_id: Optional[int]
    target_concept_name: Optional[str]
    current_concept_id: Optional[int]
    current_concept_name: Optional[str]
    
    prerequisite_gaps: list[dict[str, Any]]
    relevant_known_concepts: list[dict[str, Any]]
    learner_state_snapshots: dict[str, Any]
    misconceptions: list[dict[str, Any]]
    retrieved_material: list[dict[str, Any]]
    teaching_plan: list[str]
    conversation_context: list[dict[str, Any]]
    evidence_candidates: list[dict[str, Any]]
    
    next_action: str  # "teach_gap", "teach_target", "verify_understanding", "backtrack", "advance", "end"
    session_id: Optional[int]
    latest_response: str
    explanation_output: str
    provenance: list[dict[str, Any]]
    step_count: int
