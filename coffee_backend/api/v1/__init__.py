from fastapi import APIRouter

from coffee_backend.api.v1.coffees import router as coffees_router

router = APIRouter()
router.include_router(coffees_router, tags=["coffees"])
