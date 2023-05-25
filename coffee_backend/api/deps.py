from fastapi import Request

from coffee_backend.services.coffee import CoffeeService


async def get_coffee_service(request: Request) -> CoffeeService:
    """Extract coffee service from app state."""
    coffee_service: CoffeeService = request.app.state.coffee_service
    return coffee_service
