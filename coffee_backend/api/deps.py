from fastapi import Request

from coffee_backend.services.coffee import CoffeeService
from coffee_backend.services.rating import RatingService


async def get_coffee_service(request: Request) -> CoffeeService:
    """Extract coffee service from app state."""
    coffee_service: CoffeeService = request.app.state.coffee_service
    return coffee_service


async def get_rating_service(request: Request) -> RatingService:
    """Extract rating service from app state."""
    rating_service: RatingService = request.app.state.rating_service
    return rating_service
