"""Decay service — deterministic forgetting model.

This module implements a mathematical forgetting curve for concept retention.
Knowledge decays over time based on elapsed time since last reinforcement and
the learner's knowledge strength.

Note:
This is an explicit initial engineering approximation, not a scientifically
validated cognitive science model.
"""

from datetime import datetime, timezone
import math

from app.db.models import KnowledgeState
from app.utils.logging import get_logger

logger = get_logger("engine.decay")

# Engineering approximation constants
BASE_HALF_LIFE_DAYS = 14.0
KNOWLEDGE_STRENGTH_MULTIPLIER = 3.0
FORGETTING_IMPACT = 0.7


def compute_decay(state: KnowledgeState, now: datetime | None = None) -> float:
    """Compute current forgetting_state (0 = fresh, 1 = fully forgotten) for a KnowledgeState.

    Does NOT mutate state or database. Pure function.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    # Determine reference timestamp: most recent reinforcement, assessment, or study
    last_time = (
        state.last_reinforced_at
        or state.last_assessed_at
        or state.last_studied_at
        or state.first_seen_at
    )

    if last_time is None:
        return 0.0

    # Ensure timezone awareness
    if last_time.tzinfo is None:
        last_time = last_time.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    elapsed_seconds = (now - last_time).total_seconds()
    if elapsed_seconds <= 0:
        return 0.0

    elapsed_days = elapsed_seconds / 86400.0

    # Effective half-life in days based on knowledge strength
    # Higher knowledge_strength extends half-life up to (1 + 3.0) = 4x base half life
    effective_half_life = BASE_HALF_LIFE_DAYS * (
        1.0 + KNOWLEDGE_STRENGTH_MULTIPLIER * state.knowledge_strength
    )

    # Exponential forgetting curve: 1 - exp(-ln(2) * t / t_half)
    forgetting_state = 1.0 - math.exp(-0.693147 * elapsed_days / effective_half_life)
    return min(max(forgetting_state, 0.0), 1.0)


def compute_effective_mastery(state: KnowledgeState, now: datetime | None = None) -> float:
    """Compute effective mastery probability taking decay into account.

    Formula:
    effective_mastery = mastery_probability * (1 - forgetting_state * FORGETTING_IMPACT)
    """
    forgetting = compute_decay(state, now)
    effective = state.mastery_probability * (1.0 - forgetting * FORGETTING_IMPACT)
    return min(max(effective, 0.0), 1.0)
