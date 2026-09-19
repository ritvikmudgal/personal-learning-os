"""FastAPI router for Library and Knowledge Ingestion management."""

import shutil
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.database import get_db_session
from app.db.models import Material
from app.db.repositories.learner_repo import LearnerRepository
from app.db.repositories.material_repo import MaterialRepository
from app.domain.library import (
    DocumentChunkResponse,
    MaterialConceptResponse,
    MaterialDetailResponse,
    MaterialResponse,
    SearchResultResponse,
    SemanticSearchRequest,
)
from app.embeddings.factory import get_embedding_provider
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.validator import MaterialValidationError, validate_material_file
from app.llm.factory import get_provider as get_llm_provider
from app.services.retrieval_service import RetrievalService
from app.utils.logging import get_logger

logger = get_logger("api.library")
router = APIRouter(prefix="/library", tags=["Library & Ingestion"])


@router.post("/upload", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def upload_material(
    file: Annotated[UploadFile, File(...)],
    learner_id: Annotated[int, Form(...)],
    db: AsyncSession = Depends(get_db_session),
):
    """Upload a learning material file (PDF, TXT, MD) and start background ingestion."""
    settings = get_settings()

    # 1. Check learner profile existence
    learner_repo = LearnerRepository(db)
    learner = await learner_repo.get_by_id(learner_id)
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner profile with ID {learner_id} not found.",
        )

    # 2. Save file temporarily to disk to validate
    target_dir = settings.materials_dir / str(learner_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = file.filename or "uploaded_material.txt"
    saved_file_path = target_dir / filename

    # Avoid file overwrite by appending counter if needed
    counter = 1
    while saved_file_path.exists():
        stem = Path(filename).stem
        ext = Path(filename).suffix
        saved_file_path = target_dir / f"{stem}_{counter}{ext}"
        counter += 1

    try:
        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error("Failed to save uploaded file: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}",
        )

    # 3. Validate saved file
    try:
        file_ext = validate_material_file(
            file_path=saved_file_path,
            filename=filename,
            content_type=file.content_type,
        )
    except MaterialValidationError as e:
        if saved_file_path.exists():
            saved_file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    file_size_bytes = saved_file_path.stat().st_size
    mime_type = file.content_type or "application/octet-stream"

    # 4. Create Material database record
    material_repo = MaterialRepository(db)
    material = await material_repo.create(
        learner_id=learner_id,
        title=Path(filename).stem.replace("_", " ").title(),
        original_filename=filename,
        file_path=str(saved_file_path),
        file_type=file_ext,
        file_size_bytes=file_size_bytes,
        mime_type=mime_type,
    )
    await db.commit()
    await db.refresh(material)

    # 5. Run Ingestion Pipeline asynchronously
    embedding_provider = get_embedding_provider()
    llm_provider = get_llm_provider()
    pipeline = IngestionPipeline(
        session=db,
        embedding_provider=embedding_provider,
        llm_provider=llm_provider,
    )

    # Execute ingestion immediately
    updated_material = await pipeline.process_material(material.id)
    return MaterialResponse.model_validate(updated_material)


@router.get("/materials", response_model=list[MaterialResponse])
async def list_materials(
    learner_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """List all uploaded materials for a learner."""
    material_repo = MaterialRepository(db)
    materials = await material_repo.get_by_learner(learner_id)
    return [MaterialResponse.model_validate(m) for m in materials]


@router.get("/materials/{material_id}", response_model=MaterialDetailResponse)
async def get_material_detail(
    material_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get detailed material record including chunks and associated concepts."""
    material_repo = MaterialRepository(db)
    material = await material_repo.get_by_id(material_id, load_relations=True)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material with ID {material_id} not found.",
        )

    chunks_resp = [
        DocumentChunkResponse(
            id=c.id,
            material_id=c.material_id,
            chunk_index=c.chunk_index,
            content=c.content,
            clean_content=c.clean_content,
            start_char=c.start_char,
            end_char=c.end_char,
            page_number=c.page_number,
            section_header=c.section_header,
            token_count=c.token_count,
            has_embedding=c.embedding is not None,
            created_at=c.created_at,
        )
        for c in material.chunks
    ]

    concepts_resp = [
        MaterialConceptResponse(
            id=mc.id,
            material_id=mc.material_id,
            concept_id=mc.concept_id,
            concept_name=mc.concept.name if mc.concept else f"Concept #{mc.concept_id}",
            chunk_id=mc.chunk_id,
            relevance_score=mc.relevance_score,
            extraction_method=mc.extraction_method,
        )
        for mc in material.material_concepts
    ]

    base_val = MaterialResponse.model_validate(material).model_dump()
    return MaterialDetailResponse(**base_val, chunks=chunks_resp, associated_concepts=concepts_resp)


@router.delete("/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    material_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a material, removing disk file and database cascading records."""
    material_repo = MaterialRepository(db)
    material = await material_repo.get_by_id(material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material with ID {material_id} not found.",
        )

    # Delete disk file if it exists
    if material.file_path:
        fpath = Path(material.file_path)
        if fpath.exists():
            try:
                fpath.unlink()
            except Exception as e:
                logger.warning("Failed to delete material disk file %s: %s", fpath, str(e))

    await material_repo.delete(material_id)
    await db.commit()


@router.post("/search", response_model=list[SearchResultResponse])
async def search_materials(
    request: SemanticSearchRequest,
    learner_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Perform vector semantic search over ingested document chunks."""
    embedding_provider = get_embedding_provider()
    retrieval_service = RetrievalService(db, embedding_provider)

    results = await retrieval_service.search_semantic(
        query=request.query,
        learner_id=learner_id,
        top_k=request.top_k,
        min_score=request.min_score,
        material_ids=request.material_ids,
    )

    return [
        SearchResultResponse(
            chunk_id=r.chunk_id,
            material_id=r.material_id,
            material_title=r.material_title,
            chunk_index=r.chunk_index,
            content=r.content,
            clean_content=r.clean_content,
            page_number=r.page_number,
            section_header=r.section_header,
            similarity_score=r.similarity_score,
        )
        for r in results
    ]


@router.get("/concepts/{concept_id}/chunks", response_model=list[SearchResultResponse])
async def get_chunks_for_concept(
    concept_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get document chunks associated with a specific concept."""
    embedding_provider = get_embedding_provider()
    retrieval_service = RetrievalService(db, embedding_provider)
    results = await retrieval_service.get_chunks_for_concept(concept_id)

    return [
        SearchResultResponse(
            chunk_id=r.chunk_id,
            material_id=r.material_id,
            material_title=r.material_title,
            chunk_index=r.chunk_index,
            content=r.content,
            clean_content=r.clean_content,
            page_number=r.page_number,
            section_header=r.section_header,
            similarity_score=r.similarity_score,
        )
        for r in results
    ]
