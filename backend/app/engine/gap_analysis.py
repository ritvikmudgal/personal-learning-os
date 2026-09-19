"""Gap analysis engine — prerequisite weakness tracing."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.decay_service import compute_decay, compute_effective_mastery
from app.services.graph_service import GraphService
from app.services.learner_state_service import LearnerStateService
from app.utils.logging import get_logger

logger = get_logger("engine.gap_analysis")


@dataclass
class ConceptGapInfo:
    """Detailed learner state and gap classification for a prerequisite concept."""

    concept_id: int
    concept_name: str
    effective_mastery: float
    classification: str  # "strong", "moderate", "weak", "unknown"
    mastery_probability: float
    forgetting_state: float
    confidence: float
    depth: int  # distance from target concept in prerequisite graph


@dataclass
class GapAnalysisResult:
    """Result of prerequisite gap analysis for a target concept."""

    target_concept_id: int
    target_concept_name: str
    prerequisites: list[ConceptGapInfo] = field(default_factory=list)
    weak_prerequisites: list[ConceptGapInfo] = field(default_factory=list)
    prerequisite_edges: list[tuple[int, int]] = field(default_factory=list)
    has_gaps: bool = False


async def find_learning_gaps(
    session: AsyncSession,
    learner_id: int,
    concept_id: int,
    now: datetime | None = None,
) -> GapAnalysisResult:
    """Traverse prerequisite graph for concept_id and evaluate learner state for each prerequisite.

    Classifies prerequisites as strong, moderate, weak, or unknown based on effective_mastery after decay.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    graph_service = GraphService(session)
    state_service = LearnerStateService(session)

    target_concept = await graph_service.get_concept(concept_id)
    if not target_concept:
        raise ValueError(f"Concept {concept_id} not found")

    nodes, edges = await graph_service.get_prerequisite_subgraph(concept_id)

    # Compute graph distance/depth from target concept
    depth_map: dict[int, int] = {concept_id: 0}
    # edges are (prereq_id, target_id)
    # We want depth from concept_id backwards
    adj: dict[int, list[int]] = {}
    for src, tgt in edges:
        if tgt not in adj:
            adj[tgt] = []
        adj[tgt].append(src)

    queue = [(concept_id, 0)]
    visited_depth = {concept_id: 0}
    while queue:
        curr, d = queue.pop(0)
        for prereq in adj.get(curr, []):
            if prereq not in visited_depth or d + 1 < visited_depth[prereq]:
                visited_depth[prereq] = d + 1
                queue.append((prereq, d + 1))

    prereq_infos: list[ConceptGapInfo] = []
    weak_infos: list[ConceptGapInfo] = []

    for node in nodes:
        if node.id == concept_id:
            continue

        state = await state_service.get_state(learner_id, node.id)
        if state is None:
            classification = "unknown"
            effective_mastery = 0.0
            mastery_prob = 0.0
            forgetting = 0.0
            conf = 0.0
        else:
            forgetting = compute_decay(state, now)
            effective_mastery = compute_effective_mastery(state, now)
            mastery_prob = state.mastery_probability
            conf = state.confidence

            if effective_mastery >= 0.7:
                classification = "strong"
            elif effective_mastery >= 0.4:
                classification = "moderate"
            else:
                classification = "weak"

        depth = visited_depth.get(node.id, 1)

        gap_info = ConceptGapInfo(
            concept_id=node.id,
            concept_name=node.name,
            effective_mastery=round(effective_mastery, 4),
            classification=classification,
            mastery_probability=round(mastery_prob, 4),
            forgetting_state=round(forgetting, 4),
            confidence=round(conf, 4),
            depth=depth,
        )

        prereq_infos.append(gap_info)
        if classification in ("weak", "unknown"):
            weak_infos.append(gap_info)

    # Sort prerequisites by depth ascending (closest prerequisites first)
    prereq_infos.sort(key=lambda x: (x.depth, x.concept_name))
    weak_infos.sort(key=lambda x: (x.depth, x.concept_name))

    return GapAnalysisResult(
        target_concept_id=concept_id,
        target_concept_name=target_concept.name,
        prerequisites=prereq_infos,
        weak_prerequisites=weak_infos,
        prerequisite_edges=edges,
        has_gaps=len(weak_infos) > 0,
    )
