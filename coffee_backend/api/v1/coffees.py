from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from motor.motor_asyncio import AsyncIOMotorClientSession  # type: ignore

from coffee_backend.api.deps import get_coffee_service, get_rating_service
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas.coffee import Coffee, UpdateCoffee
from coffee_backend.services.coffee import CoffeeService
from coffee_backend.services.rating import RatingService

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


@router.get(
    "/coffees",
    status_code=200,
    summary="",
    description="""Get list of coffees""",
    response_model=List[Coffee],
)
async def _list_coffee(
    db_session: AsyncIOMotorClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
) -> List[Coffee]:
    return await coffee_service.list(db_session=db_session)


@router.get(
    "/coffees/ids",
    status_code=200,
    summary="",
    description="Get coffee by id",
    response_model=List[UUID],
)
async def _list_coffee_ids(
    db_session: AsyncIOMotorClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
) -> List[UUID]:
    """Retrieve a list of all coffee IDs.

    This endpoint returns a list of all coffee IDs in the coffee collection.

    Args:
        db_session (AsyncIOMotorClientSession): The database session object.
        coffee_service (CoffeeService): The CoffeeService dependency.

    Returns:
        List[UUID]: A list of coffee IDs.
    """

    return await coffee_service.list_ids(db_session=db_session)


@router.patch(
    "/coffees/{coffee_id}",
    status_code=200,
    summary="Endpoint to patch coffee name.",
    description="Patch coffee name. To patch ratings use rating endpoints",
    response_model=Coffee,
)
async def _patch_coffee(
    coffee_id: UUID,
    coffee: UpdateCoffee,
    db_session: AsyncIOMotorClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
) -> Coffee:
    """Patch a coffee name.

    This method can be used to patch the coffee name.

    Args:
        coffee_id (UUID): The ID of the coffee to retrieve.
        db_session (AsyncIOMotorClientSession): The database session
            object loaded via fastapi depends
        coffee_service (CoffeeService): The CoffeeService dependency loaded via
            fastapi depends

    Returns:
        Coffee: The updated coffee object

    """
    return await coffee_service.patch_coffee(
        db_session=db_session, coffee_id=coffee_id, update_coffee=coffee
    )


@router.get(
    "/coffees/{coffee_id}",
    status_code=200,
    summary="",
    description="""Get coffee by id""",
    response_model=Coffee,
)
async def _get_coffee_by_id(
    coffee_id: UUID,
    db_session: AsyncIOMotorClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
) -> Coffee:
    """
    Retrieve a coffee object by its ID.

    Args:
        coffee_id (UUID): The ID of the coffee to retrieve.
        db_session (AsyncIOMotorClientSession): The database session
            object loaded via fastapi depends
        coffee_service (CoffeeService): The CoffeeService dependency loaded via
            fastapi depends

    Returns:
        Coffee: The coffee object matching the ID.

    """
    return await coffee_service.get_by_id(
        db_session=db_session, coffee_id=coffee_id
    )


@router.delete(
    "/coffees/{coffee_id}",
    status_code=200,
    summary="",
    description="""Get coffee by id""",
)
async def _delete_coffee_by_id(
    coffee_id: UUID,
    db_session: AsyncIOMotorClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
    rating_service: RatingService = Depends(get_rating_service),
) -> Response:
    """
    Delete a coffee object by its ID and all corresponding ratings.

    Args:
        coffee_id (UUID): The ID of the coffee to retrieve.
        db_session (AsyncIOMotorClientSession): The database session
            object loaded via fastapi depends
        coffee_service (CoffeeService): The CoffeeService dependency loaded via
            fastapi depends
        rating_service (RatingService): The RatingService dependency loaded via
            fastapi depends

    Returns:
        Response: An empty response with status code 200.

    """
    await coffee_service.delete_coffee(
        db_session=db_session, coffee_id=coffee_id
    )

    await rating_service.delete_by_coffee_id(
        db_session=db_session, coffee_id=coffee_id
    )

    return Response(status_code=200)
