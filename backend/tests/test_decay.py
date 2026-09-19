"""Tests for forgetting curve and retention decay service."""

from datetime import datetime, timedelta, timezone
from app.db.models import KnowledgeState
from app.engine.decay_service import compute_decay, compute_effective_mastery


def test_zero_elapsed_time_no_decay():
    """Test that zero time elapsed produces 0 decay."""
    now = datetime.now(timezone.utc)
    state = KnowledgeState(
        learner_id=1,
        concept_id=1,
        mastery_probability=0.8,
        knowledge_strength=0.5,
        last_reinforced_at=now,
    )
    decay = compute_decay(state, now)
    assert decay == 0.0

    effective = compute_effective_mastery(state, now)
    assert effective == 0.8


def test_decay_increases_over_time():
    """Test that decay increases after 14 days."""
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=14)

    state = KnowledgeState(
        learner_id=1,
        concept_id=1,
        mastery_probability=0.8,
        knowledge_strength=0.0,  # Base half-life ~14 days
        last_reinforced_at=past,
    )

    decay = compute_decay(state, now)
    assert decay > 0.4  # After 1 half-life, decay is around ~0.5

    effective = compute_effective_mastery(state, now)
    assert effective < 0.8  # Effective mastery drops due to forgetting


def test_stronger_knowledge_decays_slower():
    """Test that higher knowledge_strength results in less decay over the same time period."""
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=14)

    weak_state = KnowledgeState(
        learner_id=1,
        concept_id=1,
        mastery_probability=0.8,
        knowledge_strength=0.0,
        last_reinforced_at=past,
    )

    strong_state = KnowledgeState(
        learner_id=1,
        concept_id=2,
        mastery_probability=0.8,
        knowledge_strength=1.0,  # Strength extends half-life significantly
        last_reinforced_at=past,
    )

    weak_decay = compute_decay(weak_state, now)
    strong_decay = compute_decay(strong_state, now)

    assert strong_decay < weak_decay
