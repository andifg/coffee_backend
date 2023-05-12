from fastapi import APIRouter

from coffee_backend.api import health

router = APIRouter()
router.include_router(health.router, prefix="/health", tags=["health"])
