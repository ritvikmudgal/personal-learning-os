"""Material repository — database operations for learning materials."""

from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Material, IngestionStatus
from app.utils.logging import get_logger

logger = get_logger("repo.material")


class MaterialRepository:
    """Repository for managing Material records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        learner_id: int,
        title: str,
        original_filename: str,
        file_path: str,
        file_type: str,
        file_size_bytes: int,
        mime_type: str,
        checksum_sha256: str | None = None,
    ) -> Material:
        """Create a new material record with PENDING status."""
        material = Material(
            learner_id=learner_id,
            title=title,
            original_filename=original_filename,
            file_path=file_path,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            mime_type=mime_type,
            checksum_sha256=checksum_sha256,
            ingestion_status=IngestionStatus.PENDING,
        )
        self.session.add(material)
        await self.session.flush()
        await self.session.refresh(material)
        logger.info("Created material record: id=%d title=%s", material.id, material.title)
        return material

    async def get_by_id(self, material_id: int, load_relations: bool = False) -> Material | None:
        """Get material by ID, optionally eager-loading chunks and material_concepts."""
        query = select(Material).where(Material.id == material_id)
        if load_relations:
            query = query.options(
                selectinload(Material.chunks),
                selectinload(Material.material_concepts),
            )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_learner(
        self, learner_id: int, status: IngestionStatus | None = None
    ) -> list[Material]:
        """Get all materials for a learner."""
        query = select(Material).where(Material.learner_id == learner_id)
        if status:
            query = query.where(Material.ingestion_status == status)
        query = query.order_by(Material.uploaded_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_status(
        self,
        material_id: int,
        status: IngestionStatus,
        error_message: str | None = None,
        total_chunks: int | None = None,
        page_count: int | None = None,
    ) -> Material | None:
        """Update ingestion status and related fields for a material."""
        material = await self.get_by_id(material_id)
        if not material:
            return None

        material.ingestion_status = status
        if error_message is not None:
            material.error_message = error_message
        if total_chunks is not None:
            material.total_chunks = total_chunks
        if page_count is not None:
            material.page_count = page_count
        if status == IngestionStatus.COMPLETED:
            material.processed_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.refresh(material)
        logger.info("Updated material status: id=%d status=%s", material.id, status.value)
        return material

    async def delete(self, material_id: int) -> bool:
        """Delete a material record and cascading chunks/concepts."""
        material = await self.get_by_id(material_id)
        if not material:
            return False
        await self.session.delete(material)
        await self.session.flush()
        logger.info("Deleted material: id=%d", material_id)
        return True
