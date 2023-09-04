from fastapi import APIRouter

from coffee_backend.api.v1.coffees import router as coffees_router
from coffee_backend.api.v1.ratings import router as ratings_router

router = APIRouter()
router.include_router(coffees_router, tags=["coffees"])
router.include_router(ratings_router, tags=["ratings"])
