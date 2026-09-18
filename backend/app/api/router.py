"""Root API router — aggregates all sub-routers."""

from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.learner import router as learner_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(learner_router)
