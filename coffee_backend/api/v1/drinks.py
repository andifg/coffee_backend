from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response
from motor.core import AgnosticClientSession

from coffee_backend.api.deps import get_coffee_service, get_drink_service
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas import CreateDrink, Drink
from coffee_backend.services.coffee import CoffeeService
from coffee_backend.services.drink import DrinkService

router = APIRouter()


@router.get(
    "/drinks",
    status_code=200,
    summary="",
    description="""Get list of all drinks""",
    response_model=List[Drink],
)
async def _list_drinks(
    db_session: AgnosticClientSession = Depends(get_db),
    drink_service: DrinkService = Depends(get_drink_service),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=5, ge=1, description="Page size"),
    first_drink_id: Optional[UUID] = None,
    coffee_id: Optional[UUID] = None,
) -> List[Drink]:
    return await drink_service.list_drinks_with_coffee_bean_information(
        db_session=db_session,
        page_size=page_size,
        page=page,
        first_id=first_drink_id,
        coffee_bean_id=coffee_id,
    )


@router.post(
    "/drinks",
    status_code=201,
    summary="",
    description="""Create new drink""",
    response_model=Drink,
)
async def _create_drink(
    create_drink: CreateDrink,
    request: Request,
    db_session: AgnosticClientSession = Depends(get_db),
    coffee_service: CoffeeService = Depends(get_coffee_service),
    drink_service: DrinkService = Depends(get_drink_service),
) -> Drink:

    if create_drink.coffee_bean_id:
        await coffee_service.get_by_id(
            db_session=db_session, coffee_id=create_drink.coffee_bean_id
        )

    drink = Drink(
        _id=create_drink.id,
        brewing_method=create_drink.brewing_method,
        rating=create_drink.rating,
        coffee_bean_id=create_drink.coffee_bean_id,
        user_id=request.state.token["sub"],
        user_name=request.state.token["preferred_username"],
        image_exists=getattr(create_drink, "image_exists", False),
    )

    return await drink_service.add_drink(db_session=db_session, drink=drink)


@router.delete(
    "/drinks/{coffee_drink_id}",
    status_code=200,
    summary="",
    description="""Delete coffee drink by id""",
)
async def _delete_coffee_drink_by_id(
    coffee_drink_id: UUID,
    db_session: AgnosticClientSession = Depends(get_db),
    drink_service: DrinkService = Depends(get_drink_service),
) -> Response:
    await drink_service.delete_drink(
        db_session=db_session, drink_id=coffee_drink_id
    )

    return Response(status_code=200)
