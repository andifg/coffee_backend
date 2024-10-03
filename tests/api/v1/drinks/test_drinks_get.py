from typing import Generator
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyDrinks, TestApp


@patch(
    "coffee_backend.services.drink.DrinkService.list_drinks_with_coffee_bean_information"
)
@pytest.mark.asyncio
async def test_api_get_drinks(
    drink_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_drinks: DummyDrinks,
    mock_security_dependency: Generator,
) -> None:
    """Test the API endpoint to retrieve a list of drinks.

    Args:
        drink_service_mock (AsyncMock): An asynchronous mock object for the
            DrinkService.list_drinks_with_coffee_bean_information method
        test_app (TestApp): An instance of the TestApp for testing.
        dummy_drinks (DummyDrinks): A fixture providing dummy drink data.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True.
    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    drink_service_mock.return_value = [
        dummy_drinks.drink_1,
        dummy_drinks.drink_2,
    ]

    response = await test_app.client.get(
        "/api/v1/drinks",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == [
        jsonable_encoder(dummy_drinks.drink_1.model_dump(by_alias=True)),
        jsonable_encoder(dummy_drinks.drink_2.model_dump(by_alias=True)),
    ]

    drink_service_mock.assert_awaited_once_with(
        db_session=get_db_mock,
        page_size=5,
        page=1,
        first_id=None,
        coffee_bean_id=None,
    )

    app.dependency_overrides = {}


@patch(
    "coffee_backend.services.drink.DrinkService.list_drinks_with_coffee_bean_information"
)
@pytest.mark.asyncio
async def test_api_get_drinks_with_query_params(
    drink_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_drinks: DummyDrinks,
    mock_security_dependency: Generator,
) -> None:
    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    drink_service_mock.return_value = [
        dummy_drinks.drink_1,
        dummy_drinks.drink_2,
    ]

    response = await test_app.client.get(
        "/api/v1/drinks?coffee_bean_id=0668fdc6-cf0d-7855-8000-24d389e2cbb7&page=1&page_size=5&first_drink_id=0668fdc7-5d12-7ddb-8000-53ff75679f05",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == [
        jsonable_encoder(dummy_drinks.drink_1.model_dump(by_alias=True)),
        jsonable_encoder(dummy_drinks.drink_2.model_dump(by_alias=True)),
    ]

    drink_service_mock.assert_awaited_once_with(
        db_session=get_db_mock,
        page_size=5,
        page=1,
        first_id=UUID("0668fdc7-5d12-7ddb-8000-53ff75679f05"),
        coffee_bean_id=None,
    )

    app.dependency_overrides = {}


@patch(
    "coffee_backend.services.drink.DrinkService.list_drinks_with_coffee_bean_information"
)
@pytest.mark.asyncio
async def test_api_get_drinks_with_emtpy_crud_response(
    drink_service_mock: AsyncMock,
    test_app: TestApp,
    mock_security_dependency: Generator,
) -> None:
    """Test the drink 'get drinks' endpoint with an empty drink database
        collection.

    Args:
        drink_service_mock (AsyncMock): A mocked DrinkService.list_drinks_with_coffee_bean_information method.
        test_app (TestApp): An instance of the TestApp class for making test
            requests.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True
    """
    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    drink_service_mock.return_value = []

    response = await test_app.client.get(
        "/api/v1/drinks",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == []

    drink_service_mock.assert_awaited_once_with(
        db_session=get_db_mock,
        page_size=5,
        page=1,
        first_id=None,
        coffee_bean_id=None,
    )

    app.dependency_overrides = {}
