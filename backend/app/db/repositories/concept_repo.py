"""Concept repository — database operations for concepts and relationships."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Concept, ConceptRelationship, RelationshipType
from app.domain.concept import ConceptCreate, ConceptRelationshipCreate
from app.utils.logging import get_logger

logger = get_logger("repo.concept")


class ConceptRepository:
    """Repository for concept CRUD and relationship management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: ConceptCreate) -> Concept:
        """Create a new concept."""
        concept = Concept(
            name=data.name,
            description=data.description,
            domain=data.domain,
            difficulty_level=data.difficulty_level,
        )
        self.session.add(concept)
        await self.session.flush()
        await self.session.refresh(concept)
        logger.info("Created concept: id=%d name=%s", concept.id, concept.name)
        return concept

    async def get_by_id(self, concept_id: int) -> Concept | None:
        """Get a concept by ID."""
        result = await self.session.execute(
            select(Concept).where(Concept.id == concept_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, domain: str | None = None) -> list[Concept]:
        """Get all concepts, optionally filtered by domain."""
        query = select(Concept)
        if domain:
            query = query.where(Concept.domain == domain)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search_by_name(self, name: str) -> list[Concept]:
        """Search concepts by name (case-insensitive partial match)."""
        result = await self.session.execute(
            select(Concept).where(Concept.name.ilike(f"%{name}%"))
        )
        return list(result.scalars().all())

    async def add_relationship(
        self, data: ConceptRelationshipCreate
    ) -> ConceptRelationship:
        """Create a relationship between two concepts."""
        rel = ConceptRelationship(
            source_concept_id=data.source_concept_id,
            target_concept_id=data.target_concept_id,
            relationship_type=RelationshipType(data.relationship_type),
            strength=data.strength,
        )
        self.session.add(rel)
        await self.session.flush()
        await self.session.refresh(rel)
        logger.info(
            "Created concept relationship: %d -[%s]-> %d",
            data.source_concept_id,
            data.relationship_type,
            data.target_concept_id,
        )
        return rel

    async def get_prerequisites(self, concept_id: int) -> list[Concept]:
        """Get all prerequisite concepts for a given concept."""
        result = await self.session.execute(
            select(Concept)
            .join(
                ConceptRelationship,
                ConceptRelationship.source_concept_id == Concept.id,
            )
            .where(
                ConceptRelationship.target_concept_id == concept_id,
                ConceptRelationship.relationship_type == RelationshipType.PREREQUISITE,
            )
        )
        return list(result.scalars().all())

    async def get_dependents(self, concept_id: int) -> list[Concept]:
        """Get all concepts that depend on the given concept as a prerequisite."""
        result = await self.session.execute(
            select(Concept)
            .join(
                ConceptRelationship,
                ConceptRelationship.target_concept_id == Concept.id,
            )
            .where(
                ConceptRelationship.source_concept_id == concept_id,
                ConceptRelationship.relationship_type == RelationshipType.PREREQUISITE,
            )
        )
        return list(result.scalars().all())
