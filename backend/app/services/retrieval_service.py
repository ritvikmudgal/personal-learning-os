"""Retrieval Service — vector similarity search and semantic document retrieval."""

from dataclasses import dataclass
from typing import Optional
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import DocumentChunk, Material
from app.db.repositories.chunk_repo import ChunkRepository
from app.db.repositories.material_concept_repo import MaterialConceptRepository
from app.embeddings.base import EmbeddingProvider
from app.utils.logging import get_logger

logger = get_logger("service.retrieval")


@dataclass
class SearchResult:
    """SearchResult object containing matched chunk, score, and material info."""
    chunk_id: int
    material_id: int
    material_title: str
    chunk_index: int
    content: str
    clean_content: str
    page_number: Optional[int]
    section_header: Optional[str]
    similarity_score: float


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two 1D float vectors."""
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


class RetrievalService:
    """Service performing semantic query search and concept lookup over document chunks."""

    def __init__(self, session: AsyncSession, embedding_provider: EmbeddingProvider):
        self.session = session
        self.embedding_provider = embedding_provider
        self.chunk_repo = ChunkRepository(session)
        self.mat_concept_repo = MaterialConceptRepository(session)

    async def search_semantic(
        self,
        query: str,
        learner_id: int,
        top_k: int = 5,
        min_score: float = 0.0,
        material_ids: list[int] | None = None,
    ) -> list[SearchResult]:
        """Perform vector semantic search for a text query.

        Args:
            query: Natural language query string.
            learner_id: Learner profile ID.
            top_k: Max number of results to return.
            min_score: Minimum cosine similarity threshold.
            material_ids: Optional list of material IDs to filter search.

        Returns:
            List of SearchResult objects sorted by score descending.
        """
        if not query or not query.strip():
            return []

        # 1. Embed query text
        query_vector = await self.embedding_provider.embed_text(query.strip())
        if not query_vector:
            return []

        # 2. Retrieve candidate chunks with embeddings
        chunks = await self.chunk_repo.get_all_with_embeddings(
            learner_id=learner_id, material_ids=material_ids
        )
        if not chunks:
            logger.info("No embedded chunks found for learner_id=%d", learner_id)
            return []

        # 3. Compute cosine similarity for each chunk
        results: list[SearchResult] = []

        for chunk in chunks:
            if not chunk.embedding:
                continue
            
            score = cosine_similarity(query_vector, chunk.embedding)
            if score >= min_score:
                material_title = chunk.material.title if chunk.material else "Untitled Material"
                results.append(
                    SearchResult(
                        chunk_id=chunk.id,
                        material_id=chunk.material_id,
                        material_title=material_title,
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        clean_content=chunk.clean_content,
                        page_number=chunk.page_number,
                        section_header=chunk.section_header,
                        similarity_score=round(score, 4),
                    )
                )

        # 4. Sort by score descending and take top_k
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        top_results = results[:top_k]

        logger.info(
            "Semantic search query='%s' returned %d results (top score=%.4f)",
            query[:30],
            len(top_results),
            top_results[0].similarity_score if top_results else 0.0,
        )

        return top_results

    async def get_chunks_for_concept(self, concept_id: int) -> list[SearchResult]:
        """Get document chunks associated with a concept ID."""
        associations = await self.mat_concept_repo.get_by_concept(concept_id)
        results: list[SearchResult] = []

        for assoc in associations:
            if assoc.chunk:
                chunk = assoc.chunk
                material_title = assoc.material.title if assoc.material else "Untitled Material"
                results.append(
                    SearchResult(
                        chunk_id=chunk.id,
                        material_id=chunk.material_id,
                        material_title=material_title,
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        clean_content=chunk.clean_content,
                        page_number=chunk.page_number,
                        section_header=chunk.section_header,
                        similarity_score=assoc.relevance_score,
                    )
                )

        return results
