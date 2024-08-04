from uuid import UUID

from fastapi import APIRouter, Depends, Response
from motor.core import AgnosticClientSession

from coffee_backend.api.deps import get_rating_service
from coffee_backend.mongo.database import get_db
from coffee_backend.services.rating import RatingService

router = APIRouter()


@router.delete(
    "/coffee_drinks/{coffee_drink_id}",
    status_code=200,
    summary="",
    description="""Delete coffee drink by id""",
)
async def _delete_coffee_drink_by_id(
    coffee_drink_id: UUID,
    db_session: AgnosticClientSession = Depends(get_db),
    rating_service: RatingService = Depends(get_rating_service),
) -> Response:
    await rating_service.delete_rating(
        db_session=db_session, rating_id=coffee_drink_id
    )

    return Response(status_code=200)
