"""Chunk repository — database operations for document chunks and vector search."""

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import DocumentChunk, Material
from app.utils.logging import get_logger

logger = get_logger("repo.chunk")


class ChunkRepository:
    """Repository for document chunks and embedding storage."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_create(self, chunks_data: list[dict]) -> list[DocumentChunk]:
        """Bulk create document chunks for a material."""
        chunks = [DocumentChunk(**data) for data in chunks_data]
        self.session.add_all(chunks)
        await self.session.flush()
        logger.info("Bulk created %d chunks", len(chunks))
        return chunks

    async def get_by_id(self, chunk_id: int) -> DocumentChunk | None:
        """Get chunk by ID."""
        result = await self.session.execute(
            select(DocumentChunk).where(DocumentChunk.id == chunk_id)
        )
        return result.scalar_one_or_none()

    async def get_by_material(self, material_id: int) -> list[DocumentChunk]:
        """Get all chunks for a material, ordered by chunk_index."""
        result = await self.session.execute(
            select(DocumentChunk)
            .where(DocumentChunk.material_id == material_id)
            .order_by(DocumentChunk.chunk_index.asc())
        )
        return list(result.scalars().all())

    async def get_all_with_embeddings(
        self, learner_id: int | None = None, material_ids: list[int] | None = None
    ) -> list[DocumentChunk]:
        """Get all chunks that have non-null embeddings, optionally filtered by learner or material IDs."""
        query = (
            select(DocumentChunk)
            .options(selectinload(DocumentChunk.material))
            .join(Material, DocumentChunk.material_id == Material.id)
            .where(DocumentChunk.embedding.is_not(None))
        )
        if learner_id is not None:
            query = query.where(Material.learner_id == learner_id)
        if material_ids:
            query = query.where(Material.id.in_(material_ids))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_embedding(
        self, chunk_id: int, embedding: list[float], model_name: str
    ) -> DocumentChunk | None:
        """Update the embedding vector for a single chunk."""
        chunk = await self.get_by_id(chunk_id)
        if not chunk:
            return None
        chunk.embedding = embedding
        chunk.embedding_model = model_name
        await self.session.flush()
        return chunk
