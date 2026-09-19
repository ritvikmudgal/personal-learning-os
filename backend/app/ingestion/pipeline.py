"""Ingestion Pipeline — orchestrates end-to-end processing of uploaded materials."""

from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import IngestionStatus, Material
from app.db.repositories.chunk_repo import ChunkRepository
from app.db.repositories.material_repo import MaterialRepository
from app.embeddings.base import EmbeddingProvider
from app.ingestion.chunker import TextChunker
from app.ingestion.concept_extractor import ConceptExtractor
from app.ingestion.concept_linker import ConceptLinker
from app.ingestion.extractors.factory import get_extractor
from app.llm.provider import LLMProvider
from app.utils.logging import get_logger

logger = get_logger("ingestion.pipeline")


class IngestionPipeline:
    """Orchestrates document extraction, chunking, embedding, concept extraction, and linking."""

    def __init__(
        self,
        session: AsyncSession,
        embedding_provider: EmbeddingProvider,
        llm_provider: LLMProvider | None = None,
    ):
        self.session = session
        self.embedding_provider = embedding_provider
        self.llm_provider = llm_provider
        self.material_repo = MaterialRepository(session)
        self.chunk_repo = ChunkRepository(session)

    async def process_material(self, material_id: int) -> Material:
        """Run the end-to-end ingestion pipeline for a material record.

        Args:
            material_id: Material database ID.

        Returns:
            Updated Material record.
        """
        settings = get_settings()
        material = await self.material_repo.get_by_id(material_id)
        if not material:
            raise ValueError(f"Material with ID {material_id} not found.")

        logger.info("Starting ingestion pipeline for material ID=%d title='%s'", material.id, material.title)

        # Step 1: Update status to PROCESSING
        await self.material_repo.update_status(material.id, IngestionStatus.PROCESSING)
        await self.session.commit()

        try:
            file_path = Path(material.file_path)

            # Step 2: Text Extraction
            extractor = get_extractor(file_path)
            doc = extractor.extract(file_path)

            # Step 3: Chunking
            chunker = TextChunker(
                chunk_size=settings.chunk_size_chars,
                chunk_overlap=settings.chunk_overlap_chars,
            )
            raw_chunks = chunker.chunk_document(doc)

            if not raw_chunks:
                raise ValueError("No text content could be extracted or chunked from document.")

            # Step 4: Save Chunks to Database
            chunks_to_create = [
                {
                    "material_id": material.id,
                    "chunk_index": c.chunk_index,
                    "content": c.content,
                    "clean_content": c.clean_content,
                    "start_char": c.start_char,
                    "end_char": c.end_char,
                    "page_number": c.page_number,
                    "section_header": c.section_header,
                    "token_count": c.token_count,
                }
                for c in raw_chunks
            ]
            db_chunks = await self.chunk_repo.bulk_create(chunks_to_create)

            # Step 5: Embeddings Generation
            clean_texts = [c.clean_content for c in db_chunks]
            embeddings = await self.embedding_provider.embed_batch(clean_texts)

            for chunk_obj, emb_vec in zip(db_chunks, embeddings):
                await self.chunk_repo.update_embedding(
                    chunk_id=chunk_obj.id,
                    embedding=emb_vec,
                    model_name=self.embedding_provider.model_name,
                )

            # Step 6 & 7: Concept Extraction & Linking (if LLM provider available)
            if self.llm_provider:
                concept_extractor = ConceptExtractor(self.llm_provider)
                concept_linker = ConceptLinker(self.session)

                # Process concepts for top chunks (up to 10 chunks to avoid excessive LLM calls on Mac)
                sample_chunks = db_chunks[:10]
                for chunk_obj in sample_chunks:
                    ext_concepts = await concept_extractor.extract_concepts_from_chunk(
                        chunk_obj.clean_content
                    )
                    if ext_concepts:
                        await concept_linker.link_extracted_concepts(
                            material_id=material.id,
                            chunk_id=chunk_obj.id,
                            extracted_concepts=ext_concepts,
                        )

            # Step 8: Mark COMPLETED
            updated_material = await self.material_repo.update_status(
                material_id=material.id,
                status=IngestionStatus.COMPLETED,
                total_chunks=len(db_chunks),
                page_count=doc.total_pages,
            )
            await self.session.commit()

            logger.info(
                "Ingestion pipeline completed successfully for material ID=%d (%d chunks, %d pages)",
                material.id,
                len(db_chunks),
                doc.total_pages,
            )
            return updated_material

        except Exception as e:
            await self.session.rollback()
            error_msg = str(e)
            logger.error("Ingestion pipeline failed for material ID=%d: %s", material_id, error_msg, exc_info=True)

            failed_material = await self.material_repo.update_status(
                material_id=material_id,
                status=IngestionStatus.FAILED,
                error_message=error_msg,
            )
            await self.session.commit()
            return failed_material
