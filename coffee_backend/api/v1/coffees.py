from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.security import OAuth2PasswordBearer
from motor.core import AgnosticClientSession

from coffee_backend.api.authorization import authorize_coffee_edit_delete
from coffee_backend.api.deps import (
    get_coffee_images_service,
    get_coffee_service,
    get_rating_service,
)
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas.coffee import Coffee, CreateCoffee, UpdateCoffee
from coffee_backend.services.coffee import CoffeeService
from coffee_backend.services.coffee_image import ImageService
from coffee_backend.services.rating import RatingService

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post(
    "/coffees/",
    status_code=201,
    summary="",
    description="""""",
    response_model=Coffee,
)
async def _post_coffee(
    create_coffee: CreateCoffee,
    request: Request,
    db_session: AgnosticClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
) -> Coffee:
    coffee = Coffee(
        **create_coffee.model_dump(by_alias=True),
        owner_id=request.state.token["sub"],
        owner_name=request.state.token["preferred_username"]
    )
    return await coffee_service.add_coffee(coffee=coffee, db_session=db_session)


@router.get(
    "/coffees",
    status_code=200,
    summary="",
    description="""Get list of coffees including rating summary""",
    response_model=List[Coffee],
)
async def _list_coffees_with_rating_summary(
    db_session: AgnosticClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, description="Page size"),
    owner_id: Optional[UUID] = None,
    first_id: Optional[UUID] = None,
) -> List[Coffee]:
    return await coffee_service.list_coffees_with_rating_summary(
        db_session=db_session,
        page=page,
        page_size=page_size,
        owner_id=owner_id,
        first_id=first_id,
    )


@router.get(
    "/coffees/ids",
    status_code=200,
    summary="",
    description="Get coffee by id",
    response_model=List[UUID],
)
async def _list_coffee_ids(
    db_session: AgnosticClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
) -> List[UUID]:
    """Retrieve a list of all coffee IDs.

    This endpoint returns a list of all coffee IDs in the coffee collection.

    Args:
        db_session (AgnosticClientSession): The database session object.
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
    request: Request,
    db_session: AgnosticClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
) -> Coffee:
    """Patch a coffee name.

    This method can be used to patch the coffee name.

    Args:
        coffee_id (UUID): The ID of the coffee to retrieve.
        db_session (AgnosticClientSession): The database session
            object loaded via fastapi depends
        coffee_service (CoffeeService): The CoffeeService dependency loaded via
            fastapi depends

    Returns:
        Coffee: The updated coffee object

    """
    authorize_coffee_edit_delete(request, coffee.owner_id)

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
    db_session: AgnosticClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
) -> Coffee:
    """
    Retrieve a coffee object by its ID.

    Args:
        coffee_id (UUID): The ID of the coffee to retrieve.
        db_session (AgnosticClientSession): The database session
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
    request: Request,
    db_session: AgnosticClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
    rating_service: RatingService = Depends(get_rating_service),
    image_service: ImageService = Depends(get_coffee_images_service),
) -> Response:
    """
    Delete a coffee object by its ID and all corresponding ratings.

    Args:
        coffee_id (UUID): The ID of the coffee to retrieve.
        db_session (AgnosticClientSession): The database session
            object loaded via fastapi depends
        coffee_service (CoffeeService): The CoffeeService dependency loaded via
            fastapi depends
        rating_service (RatingService): The RatingService dependency loaded via
            fastapi depends

    Returns:
        Response: An empty response with status code 200.

    """
    coffee_to_delete = await coffee_service.get_by_id(
        db_session=db_session, coffee_id=coffee_id
    )

    authorize_coffee_edit_delete(request, coffee_to_delete.owner_id)

    await rating_service.delete_by_coffee_id(
        db_session=db_session, coffee_id=coffee_id
    )

    image_service.delete_coffee_image(coffee_id=coffee_id)

    await coffee_service.delete_coffee(
        db_session=db_session, coffee_id=coffee_id
    )

    return Response(status_code=200)
