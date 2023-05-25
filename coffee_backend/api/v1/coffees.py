from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClientSession  # type: ignore

from coffee_backend.api.deps import get_coffee_service
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas.coffee import Coffee
from coffee_backend.services.coffee import CoffeeService

router = APIRouter()


@router.post(
    "/coffees/",
    status_code=201,
    summary="",
    description="""""",
    response_model=Coffee,
)
async def _post_coffee(
    coffee: Coffee,
    db_session: AsyncIOMotorClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
) -> Coffee:

    return await coffee_service.add_coffee(coffee=coffee, db_session=db_session)
