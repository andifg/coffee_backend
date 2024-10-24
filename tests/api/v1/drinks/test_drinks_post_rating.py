import copy
from typing import Generator
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas import CreateDrink
from tests.conftest import DummyDrinks, TestApp


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@patch("coffee_backend.services.drink.DrinkService.add_drink")
@pytest.mark.asyncio
async def test_api_create_drink_with_existing_coffee_bean_id(
    drink_service_mock: AsyncMock,
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_drinks: DummyDrinks,
    mock_security_dependency: Generator,
) -> None:
    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.return_value = {}

    drink_service_mock.return_value = dummy_drinks.drink_1.model_dump(
        by_alias=True
    )

    create_drink = CreateDrink(
        _id=dummy_drinks.drink_1.id,
        rating=dummy_drinks.drink_1.rating,
        brewing_method=dummy_drinks.drink_1.brewing_method,
        coffee_bean_id=dummy_drinks.drink_1.coffee_bean_id,
        image_exists=dummy_drinks.drink_1.image_exists,
        coordinate=dummy_drinks.drink_1.coordinate,
    )

    create_coffee_jsonable = jsonable_encoder(
        create_drink.model_dump(by_alias=True)
    )

    response = await test_app.client.post(
        f"/api/v1/drinks",
        json=create_coffee_jsonable,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 201
    assert response.json() == jsonable_encoder(
        dummy_drinks.drink_1.model_dump(by_alias=True)
    )

    drink_service_mock.assert_awaited_once_with(
        drink=dummy_drinks.drink_1, db_session=get_db_mock
    )

    app.dependency_overrides = {}


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@pytest.mark.asyncio
async def test_api_create_drink_with_not_existing_coffee_bean_id(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_drinks: DummyDrinks,
    mock_security_dependency: Generator,
) -> None:
    coffee_service_mock.side_effect = HTTPException(
        status_code=404, detail="No coffee found for given id"
    )

    create_drink = CreateDrink(
        _id=dummy_drinks.drink_1.id,
        rating=dummy_drinks.drink_1.rating,
        brewing_method=dummy_drinks.drink_1.brewing_method,
        coffee_bean_id=dummy_drinks.drink_1.coffee_bean_id,
        coordinate=dummy_drinks.drink_1.coordinate,
    )

    create_coffee_jsonable = jsonable_encoder(
        create_drink.model_dump(by_alias=True)
    )

    response = await test_app.client.post(
        f"/api/v1/drinks",
        json=create_coffee_jsonable,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404


@patch("coffee_backend.services.drink.DrinkService.add_drink")
@pytest.mark.asyncio
async def test_api_create_drink_without_coffee_bean_reference(
    drink_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_drinks: DummyDrinks,
    mock_security_dependency: Generator,
) -> None:
    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    expected_drink = copy.deepcopy(dummy_drinks.drink_2)

    expected_drink.user_name = "Jdoe"
    expected_drink.user_id = UUID("018ee105-66b3-7f89-b6f3-807782e40350")

    drink_service_mock.return_value = expected_drink.model_dump(by_alias=True)

    create_drink = CreateDrink(
        _id=dummy_drinks.drink_2.id,
        brewing_method=dummy_drinks.drink_2.brewing_method,
        rating=dummy_drinks.drink_2.rating,
        image_exists=dummy_drinks.drink_2.image_exists,
        coordinate=dummy_drinks.drink_2.coordinate,
    )

    create_coffee_jsonable = jsonable_encoder(
        create_drink.model_dump(by_alias=True)
    )

    response = await test_app.client.post(
        f"/api/v1/drinks",
        json=create_coffee_jsonable,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 201
    assert response.json() == jsonable_encoder(expected_drink)

    drink_service_mock.assert_awaited_once_with(
        drink=expected_drink, db_session=get_db_mock
    )

    app.dependency_overrides = {}
