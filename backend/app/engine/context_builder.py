"""Context builder service — prioritized context budget assembler for small local models (qwen2.5:3b).

Ensures the LLM receives structured, highly relevant, token-capped context without
exceeding local LLM memory budgets (~1500-2000 tokens / ~6000-8000 chars).
"""

from dataclasses import dataclass, field
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.gap_analysis import find_learning_gaps, GapAnalysisResult
from app.embeddings.factory import get_embedding_provider
from app.services.learner_state_service import LearnerStateService
from app.services.misconception_service import MisconceptionService
from app.services.retrieval_service import RetrievalService
from app.services.graph_service import GraphService
from app.utils.logging import get_logger

logger = get_logger("engine.context_builder")


@dataclass
class ProvenanceItem:
    """Provenance indicator for materials, prerequisites, or misconceptions used in context."""
    source_type: str  # "prerequisite", "material", "misconception", "prior_knowledge"
    title: str
    detail: str


@dataclass
class BuiltContext:
    """Assembled context budget container for tutor generation."""
    target_concept_name: str
    formatted_context_str: str
    provenance_list: list[ProvenanceItem] = field(default_factory=list)
    has_weak_prereqs: bool = False
    weak_prereq_names: list[str] = field(default_factory=list)
    active_misconceptions: list[str] = field(default_factory=list)
    material_chunks_used: list[dict[str, Any]] = field(default_factory=list)


class ContextBuilderService:
    """Service for constructing token-budgeted prompt context for LLM tutor operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.state_service = LearnerStateService(session)
        self.misconception_service = MisconceptionService(session)
        self.retrieval_service = RetrievalService(session, embedding_provider=get_embedding_provider())
        self.graph_service = GraphService(session)

    async def build_tutor_context(
        self,
        learner_id: int,
        target_concept_id: int | None,
        target_concept_name: str,
        user_message: str,
        recent_history: list[dict[str, Any]] | None = None,
        max_char_limit: int = 7000,
    ) -> BuiltContext:
        """Build prioritized context string and provenance tags for qwen2.5:3b."""
        provenance: list[ProvenanceItem] = []
        weak_prereq_names: list[str] = []
        misconception_texts: list[str] = []
        material_chunks: list[dict[str, Any]] = []

        sections: list[str] = []
        current_len = 0

        # 1. Target Concept & Focus
        target_sec = f"=== CURRENT TARGET CONCEPT ===\nConcept: {target_concept_name}\nUser Message: {user_message}"
        sections.append(target_sec)
        current_len += len(target_sec)

        # 2. Prerequisite Gap Analysis & Learner State
        if target_concept_id is not None:
            try:
                gap_result: GapAnalysisResult = await find_learning_gaps(
                    session=self.session,
                    learner_id=learner_id,
                    concept_id=target_concept_id,
                )
                if gap_result.has_gaps:
                    weak_names = [p.concept_name for p in gap_result.weak_prerequisites]
                    weak_prereq_names.extend(weak_names)
                    prereq_sec = "=== PREREQUISITE GAPS DETECTED ===\nThe following prerequisite concepts are weak or unstudied:\n"
                    for wp in gap_result.weak_prerequisites[:3]:
                        prereq_sec += f"- {wp.concept_name} (Effective Mastery: {wp.effective_mastery * 100:.0f}%, Classification: {wp.classification})\n"
                        provenance.append(
                            ProvenanceItem(
                                source_type="prerequisite",
                                title=wp.concept_name,
                                detail=f"Weak prerequisite ({wp.classification})",
                            )
                        )
                    sections.append(prereq_sec)
                    current_len += len(prereq_sec)

                # Strong prerequisites for reactivation
                strong_prereqs = [p for p in gap_result.prerequisites if p.classification == "strong"]
                if strong_prereqs:
                    strong_sec = "=== RELEVANT PRIOR KNOWLEDGE ===\nThe learner has strong mastery in these related prerequisites:\n"
                    for sp in strong_prereqs[:3]:
                        strong_sec += f"- {sp.concept_name} (Mastery: {sp.mastery_probability * 100:.0f}%)\n"
                        provenance.append(
                            ProvenanceItem(
                                source_type="prior_knowledge",
                                title=sp.concept_name,
                                detail="Strong prior concept",
                            )
                        )
                    sections.append(strong_sec)
                    current_len += len(strong_sec)

            except Exception as e:
                logger.warning("Error running gap analysis for concept %s: %s", target_concept_id, e)

        # 3. Active Misconceptions
        try:
            misc_list = await self.misconception_service.get_active_misconceptions(
                learner_id=learner_id,
                concept_id=target_concept_id,
            )
            if misc_list:
                misc_sec = "=== ACTIVE LEARNER MISCONCEPTIONS ===\n"
                for m in misc_list[:2]:
                    misc_text = m.description
                    misconception_texts.append(misc_text)
                    misc_sec += f"- {misc_text} (Severity: {m.severity})\n"
                    provenance.append(
                        ProvenanceItem(
                            source_type="misconception",
                            title="Flagged Misconception",
                            detail=misc_text[:60],
                        )
                    )
                sections.append(misc_sec)
                current_len += len(misc_sec)
        except Exception as e:
            logger.warning("Error fetching misconceptions: %s", e)

        # 4. Relevant Material (RAG)
        try:
            from app.utils.query_cleaner import build_clean_search_query

            search_query = build_clean_search_query(target_concept_name, user_message)
            retrieval_results = await self.retrieval_service.search_semantic(
                query=search_query,
                learner_id=learner_id,
                top_k=3,
                min_score=0.3,
            )
            if retrieval_results:
                rag_sec = "=== RELEVANT UPLOADED LIBRARY MATERIAL ===\n"
                for res in retrieval_results[:2]:
                    chunk_text = res.clean_content[:400]
                    page_info = f" (Page {res.page_number})" if res.page_number else ""
                    sec_info = f" [{res.section_header}]" if res.section_header else ""
                    rag_sec += f"Source: '{res.material_title}'{page_info}{sec_info}\nExcerpt: \"{chunk_text}...\"\n\n"
                    
                    material_chunks.append({
                        "chunk_id": res.chunk_id,
                        "material_id": res.material_id,
                        "material_title": res.material_title,
                        "page_number": res.page_number,
                        "section_header": res.section_header,
                        "score": res.similarity_score,
                    })
                    provenance.append(
                        ProvenanceItem(
                            source_type="material",
                            title=res.material_title,
                            detail=f"Library Material{page_info}",
                        )
                    )
                sections.append(rag_sec)
                current_len += len(rag_sec)
        except Exception as e:
            logger.warning("Error running retrieval for context: %s", e)

        # 5. Recent Conversation Turns
        if recent_history:
            history_sec = "=== RECENT CONVERSATION HISTORY ===\n"
            for turn in recent_history[-4:]:
                sender = turn.get("sender", "user").capitalize()
                text = turn.get("text", "")[:300]
                history_sec += f"{sender}: {text}\n"
            sections.append(history_sec)

        full_formatted = "\n\n".join(sections)
        if len(full_formatted) > max_char_limit:
            full_formatted = full_formatted[:max_char_limit] + "\n... [Context truncated to fit model budget]"

        return BuiltContext(
            target_concept_name=target_concept_name,
            formatted_context_str=full_formatted,
            provenance_list=provenance,
            has_weak_prereqs=len(weak_prereq_names) > 0,
            weak_prereq_names=weak_prereq_names,
            active_misconceptions=misconception_texts,
            material_chunks_used=material_chunks,
        )
