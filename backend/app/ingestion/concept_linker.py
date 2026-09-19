"""Concept linker for connecting extracted concepts to the Knowledge Graph."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MaterialConcept, Concept
from app.db.repositories.concept_repo import ConceptRepository
from app.db.repositories.material_concept_repo import MaterialConceptRepository
from app.domain.concept import ConceptCreate
from app.ingestion.concept_extractor import ExtractedConcept
from app.utils.logging import get_logger

logger = get_logger("ingestion.concept_linker")


class ConceptLinker:
    """Links extracted document concepts with existing concept graph nodes or creates new ones."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.concept_repo = ConceptRepository(session)
        self.mat_concept_repo = MaterialConceptRepository(session)

    async def link_extracted_concepts(
        self,
        material_id: int,
        chunk_id: int | None,
        extracted_concepts: list[ExtractedConcept],
    ) -> list[MaterialConcept]:
        """Link a set of extracted concepts for a material/chunk to DB concepts.

        Args:
            material_id: Material database ID.
            chunk_id: DocumentChunk database ID (optional).
            extracted_concepts: List of ExtractedConcept objects.

        Returns:
            List of MaterialConcept association records created.
        """
        associations: list[MaterialConcept] = []
        linked_concept_ids: set[int] = set()

        for ext in extracted_concepts:
            # 1. Search for existing concept by exact/case-insensitive name
            existing_concepts = await self.concept_repo.search_by_name(ext.name)
            target_concept: Concept | None = None

            for candidate in existing_concepts:
                if candidate.name.strip().lower() == ext.name.strip().lower():
                    target_concept = candidate
                    break

            # 2. If no match found, create new Concept node
            if not target_concept:
                create_data = ConceptCreate(
                    name=ext.name,
                    description=ext.description,
                    domain=ext.domain,
                    difficulty_level=ext.difficulty_level,
                )
                target_concept = await self.concept_repo.create(create_data)
                logger.info("Created new Concept node during ingestion: id=%d name='%s'", target_concept.id, target_concept.name)

            # 3. Deduplicate concept associations per (material_id, chunk_id, concept_id)
            if target_concept.id in linked_concept_ids and chunk_id is None:
                continue

            # 4. Create MaterialConcept association
            association = await self.mat_concept_repo.create(
                material_id=material_id,
                concept_id=target_concept.id,
                chunk_id=chunk_id,
                relevance_score=ext.relevance_score,
                extraction_method="llm",
            )
            associations.append(association)
            linked_concept_ids.add(target_concept.id)

        return associations
