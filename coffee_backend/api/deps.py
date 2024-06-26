from fastapi import Request

from coffee_backend.s3.object import ObjectCRUD
from coffee_backend.services.coffee import CoffeeService
from coffee_backend.services.image_service import ImageService
from coffee_backend.services.rating import RatingService


async def get_coffee_service(request: Request) -> CoffeeService:
    """Extract coffee service from app state."""
    coffee_service: CoffeeService = request.app.state.coffee_service
    return coffee_service


async def get_rating_service(request: Request) -> RatingService:
    """Extract rating service from app state."""
    rating_service: RatingService = request.app.state.rating_service
    return rating_service


async def get_object_crud(request: Request) -> ObjectCRUD:
    """Extract object crud from app state."""
    object_crud: ObjectCRUD = request.app.state.object_crud
    return object_crud


async def get_coffee_images_service(request: Request) -> ImageService:
    """Extract coffee images service from app state."""
    coffee_images_service: ImageService = (
        request.app.state.coffee_images_service
    )
    return coffee_images_service
