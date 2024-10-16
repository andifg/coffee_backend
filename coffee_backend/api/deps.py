from fastapi import Request

from coffee_backend.metrics import DailyActiveUsersMetric
from coffee_backend.s3.object import ObjectCRUD
from coffee_backend.services.coffee import CoffeeService
from coffee_backend.services.drink import DrinkService
from coffee_backend.services.image_service import ImageService


async def get_coffee_service(request: Request) -> CoffeeService:
    """Extract coffee service from app state."""
    coffee_service: CoffeeService = request.app.state.coffee_service
    return coffee_service


async def get_drink_service(request: Request) -> DrinkService:
    """Extract rating service from app state."""
    drink_service: DrinkService = request.app.state.drink_service
    return drink_service


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


async def get_unique_user_metric(request: Request) -> DailyActiveUsersMetric:
    """Extract unique user metric from app state."""
    unique_user_metric: DailyActiveUsersMetric = (
        request.app.state.daily_active_users_metric
    )
    return unique_user_metric
