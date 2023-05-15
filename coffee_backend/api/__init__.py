from fastapi import APIRouter

from coffee_backend.api import health
from coffee_backend.api.v1 import router as api_router

router = APIRouter()
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(api_router, prefix="/api/v1")
