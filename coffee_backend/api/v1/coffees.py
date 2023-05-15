from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClientSession  # type: ignore

from coffee_backend.mongo.database import get_db
from coffee_backend.schemas.coffee import Coffee

router = APIRouter()


@router.post(
    "/coffees/",
    status_code=201,
    summary="",
    description="""""",
    response_model=Coffee,
)
async def _post_coffee(
    coffee: Coffee, db_session: AsyncIOMotorClientSession = Depends(get_db)
) -> Coffee:

    print(db_session)

    return coffee
