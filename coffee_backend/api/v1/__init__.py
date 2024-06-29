from fastapi import APIRouter

from coffee_backend.api.v1.coffee_drink_image import (
    router as coffee_drink_images_router,
)
from coffee_backend.api.v1.coffee_image import router as coffee_images_router
from coffee_backend.api.v1.coffees import router as coffees_router
from coffee_backend.api.v1.ratings import router as ratings_router

router = APIRouter()
router.include_router(coffees_router, tags=["coffees"])
router.include_router(ratings_router, tags=["ratings"])
router.include_router(coffee_images_router, tags=["coffee_images"])
router.include_router(coffee_drink_images_router, tags=["coffee_drink_images"])
