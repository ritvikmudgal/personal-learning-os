"""Core learning engine package.

Contains deterministic algorithms for:
- Knowledge state updates from evidence
- Retention and forgetting curves
- Prerequisite gap analysis
"""

from app.engine.decay_service import compute_decay, compute_effective_mastery
from app.engine.gap_analysis import ConceptGapInfo, GapAnalysisResult, find_learning_gaps
from app.engine.update_engine import update_state_from_evidence

__all__ = [
    "compute_decay",
    "compute_effective_mastery",
    "update_state_from_evidence",
    "find_learning_gaps",
    "ConceptGapInfo",
    "GapAnalysisResult",
]
