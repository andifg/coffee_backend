from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from motor.core import AgnosticClientSession

from coffee_backend.api.deps import get_coffee_service, get_rating_service
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas.rating import Rating
from coffee_backend.schemas.rating_summary import RatingSummary
from coffee_backend.services.coffee import CoffeeService
from coffee_backend.services.rating import RatingService

router = APIRouter()


@router.get(
    "/ratings",
    status_code=200,
    summary="",
    description="""Get list of all ratings""",
    response_model=List[Rating],
)
async def _list_ratings(
    db_session: AgnosticClientSession = Depends(get_db),
    rating_service: RatingService = Depends(get_rating_service),
) -> List[Rating]:
    return await rating_service.list(db_session=db_session)


@router.delete(
    "/coffees/{coffee_id}/ratings/{rating_id}",
    status_code=200,
    summary="",
    description="""Get list of all ratings""",
)
async def _delete_rating(
    rating_id: UUID,
    coffee_id: UUID,
    db_session: AgnosticClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
    rating_service: RatingService = Depends(get_rating_service),
) -> Response:
    await coffee_service.get_by_id(db_session=db_session, coffee_id=coffee_id)
    await rating_service.delete_rating(
        db_session=db_session, rating_id=rating_id
    )

    return Response(status_code=200)


@router.get(
    "/coffees/{coffee_id}/rating-ids",
    status_code=200,
    summary="",
    description="""Get list of all ratings""",
    response_model=List[UUID],
)
async def _list_coffees_ratings_ids(
    coffee_id: UUID,
    db_session: AgnosticClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
    rating_service: RatingService = Depends(get_rating_service),
) -> List[UUID]:
    await coffee_service.get_by_id(db_session=db_session, coffee_id=coffee_id)
    return await rating_service.list_ids_for_coffee(
        db_session=db_session, coffee_id=coffee_id
    )


@router.get(
    "/coffees/{coffee_id}/rating-summary",
    status_code=200,
    summary="",
    description="""Get list of all ratings""",
    response_model=RatingSummary,
)
async def _get_coffees_rating_summary(
    coffee_id: UUID,
    db_session: AgnosticClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
    rating_service: RatingService = Depends(get_rating_service),
) -> RatingSummary:
    await coffee_service.get_by_id(db_session=db_session, coffee_id=coffee_id)
    return await rating_service.create_rating_summary_for_coffee(
        db_session=db_session, coffee_id=coffee_id
    )


@router.post(
    "/coffees/{coffee_id}/ratings",
    status_code=200,
    summary="",
    description="""Get list of all ratings""",
    response_model=Rating,
)
async def _create_coffee_rating(
    coffee_id: UUID,
    rating: Rating,
    db_session: AgnosticClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
    rating_service: RatingService = Depends(get_rating_service),
) -> Rating:
    await coffee_service.get_by_id(db_session=db_session, coffee_id=coffee_id)
    return await rating_service.add_rating(db_session=db_session, rating=rating)
