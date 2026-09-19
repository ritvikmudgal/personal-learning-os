"""Knowledge-state update engine — deterministic state updates from learning evidence.

This module implements the core state update logic when new evidence is recorded.
All formulas and constants are explicit engineering approximations.
"""

from datetime import datetime, timezone

from app.db.models import Evidence, EvidenceType, KnowledgeState
from app.utils.logging import get_logger

logger = get_logger("engine.update")

# Engineering approximation constants
LEARNING_RATE = 0.12
STRENGTH_INCREMENT = 0.05
STRENGTH_DECREMENT = 0.08
RELIABILITY_INCREMENT = 0.03
REINFORCEMENT_THRESHOLD = 0.6


def update_state_from_evidence(
    state: KnowledgeState, evidence: Evidence, now: datetime | None = None
) -> KnowledgeState:
    """Update a KnowledgeState in-place based on a new Evidence record.

    Returns the updated KnowledgeState instance.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    # 1. Update mastery_probability
    difficulty = evidence.difficulty if evidence.difficulty is not None else 0.5
    difficulty_weight = 0.8 + 0.4 * difficulty
    target = evidence.result_quality * difficulty_weight
    delta = LEARNING_RATE * (target - state.mastery_probability)
    state.mastery_probability = min(max(state.mastery_probability + delta, 0.0), 1.0)

    # 2. Update knowledge_strength
    if evidence.result_quality >= 0.7:
        state.knowledge_strength = min(1.0, state.knowledge_strength + STRENGTH_INCREMENT)
    elif evidence.result_quality < 0.4:
        state.knowledge_strength = max(0.0, state.knowledge_strength - STRENGTH_DECREMENT)

    # 3. Update confidence ONLY if explicit confidence data is in evidence
    if evidence.confidence is not None:
        state.confidence = min(
            max(0.7 * state.confidence + 0.3 * evidence.confidence, 0.0), 1.0
        )

    # 4. Update evidence_reliability
    state.evidence_reliability = min(1.0, state.evidence_reliability + RELIABILITY_INCREMENT)

    # 5. Timestamps & forgetting_state reset
    state.last_studied_at = now

    assessment_types = {
        EvidenceType.ASSESSMENT_ANSWER,
        EvidenceType.SOLVED_PROBLEM,
        EvidenceType.REPEATED_SUCCESS,
        EvidenceType.REPEATED_FAILURE,
    }
    if evidence.evidence_type in assessment_types:
        state.last_assessed_at = now

    if evidence.result_quality >= REINFORCEMENT_THRESHOLD:
        state.last_reinforced_at = now
        state.forgetting_state = 0.0

    logger.debug(
        "State updated for concept %d: mastery=%.3f, strength=%.3f",
        state.concept_id,
        state.mastery_probability,
        state.knowledge_strength,
    )
    return state
