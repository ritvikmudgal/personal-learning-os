"""Root API router — aggregates all sub-routers."""

from fastapi import APIRouter

from app.api.concepts import router as concepts_router
from app.api.health import router as health_router
from app.api.knowledge import router as knowledge_router
from app.api.learner import router as learner_router
from app.api.library import router as library_router
from app.api.settings import router as settings_router
from app.api.tutor import tutor_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(learner_router)
api_router.include_router(concepts_router)
api_router.include_router(knowledge_router)
api_router.include_router(library_router)
api_router.include_router(tutor_router)
api_router.include_router(settings_router)


