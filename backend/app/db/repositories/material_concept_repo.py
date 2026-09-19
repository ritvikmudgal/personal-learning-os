"""MaterialConcept repository — database operations linking materials/chunks to concepts."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import MaterialConcept, Concept, DocumentChunk
from app.utils.logging import get_logger

logger = get_logger("repo.material_concept")


class MaterialConceptRepository:
    """Repository for managing MaterialConcept associations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        material_id: int,
        concept_id: int,
        chunk_id: int | None = None,
        relevance_score: float = 1.0,
        extraction_method: str = "llm",
    ) -> MaterialConcept:
        """Link a material (and optional chunk) to a concept."""
        association = MaterialConcept(
            material_id=material_id,
            concept_id=concept_id,
            chunk_id=chunk_id,
            relevance_score=relevance_score,
            extraction_method=extraction_method,
        )
        self.session.add(association)
        await self.session.flush()
        await self.session.refresh(association)
        return association

    async def get_by_material(self, material_id: int) -> list[MaterialConcept]:
        """Get all concept associations for a material with loaded concepts."""
        result = await self.session.execute(
            select(MaterialConcept)
            .options(selectinload(MaterialConcept.concept))
            .where(MaterialConcept.material_id == material_id)
        )
        return list(result.scalars().all())

    async def get_by_concept(self, concept_id: int) -> list[MaterialConcept]:
        """Get all material associations for a concept."""
        result = await self.session.execute(
            select(MaterialConcept)
            .options(
                selectinload(MaterialConcept.material),
                selectinload(MaterialConcept.chunk),
            )
            .where(MaterialConcept.concept_id == concept_id)
        )
        return list(result.scalars().all())
