from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response
from motor.core import AgnosticClientSession

from coffee_backend.api.deps import get_coffee_service, get_rating_service
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas import CreateRating, Rating
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
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=5, ge=1, description="Page size"),
    first_rating_id: Optional[UUID] = None,
    coffee_id: Optional[UUID] = None,
) -> List[Rating]:
    return await rating_service.list(
        db_session=db_session,
        coffee_id=coffee_id,
        page_size=page_size,
        page=page,
        first_rating_id=first_rating_id,
    )


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


@router.post(
    "/coffees/{coffee_id}/ratings",
    status_code=201,
    summary="",
    description="""Get list of all ratings""",
    response_model=Rating,
)
async def _create_coffee_rating(
    create_rating: CreateRating,
    request: Request,
    db_session: AgnosticClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
    rating_service: RatingService = Depends(get_rating_service),
) -> Rating:
    await coffee_service.get_by_id(
        db_session=db_session, coffee_id=create_rating.coffee_id
    )

    rating = Rating(
        _id=create_rating.id,
        brewing_method=create_rating.brewing_method,
        rating=create_rating.rating,
        coffee_id=create_rating.coffee_id,
        user_id=request.state.token["sub"],
        user_name=request.state.token["preferred_username"],
        image_exists=getattr(create_rating, "image_exists", False),
    )

    return await rating_service.add_rating(db_session=db_session, rating=rating)
