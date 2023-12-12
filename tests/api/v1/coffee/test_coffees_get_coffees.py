from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyCoffees, TestApp


@patch("coffee_backend.services.coffee.CoffeeService.list")
@pytest.mark.asyncio
async def test_api_get_coffees(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_coffees: DummyCoffees,
    mock_security_dependency: Generator,
) -> None:
    """Test coffees endpoint get method.

    Args:
        coffee_service_mock (AsyncMock): A mocked CoffeeService.list method.
        test_app (TestApp): An instance of the TestApp class for making test
            requests.
        dummy_coffees (DummyCoffees): The dummy coffees fixture.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True.

    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.return_value = [
        dummy_coffees.coffee_1.dict(by_alias=True),
        dummy_coffees.coffee_2.dict(by_alias=True),
    ]

    response = await test_app.client.get(
        "/api/v1/coffees",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == [
        jsonable_encoder(dummy_coffees.coffee_1.dict(by_alias=True)),
        jsonable_encoder(dummy_coffees.coffee_2.dict(by_alias=True)),
    ]

    coffee_service_mock.assert_awaited_once_with(db_session=get_db_mock)

    app.dependency_overrides = {}


@patch("coffee_backend.services.coffee.CoffeeService.list")
@pytest.mark.asyncio
async def test_api_get_coffees_with_emtpy_crud_response(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    mock_security_dependency: Generator,
) -> None:
    """Test the coffee 'get coffees' endpoint with an empty coffee database
        collection.

    Ensures that the '/api/v1/coffees' endpoint behaves correctly when the
    coffee database collection is empty. The test mocks the CoffeeService.list
    method to simulate a 404 error with the detail message 'No coffees found'.
    It verifies that the response has a status code of 404 and a JSON body with
    the expected detail message.

    Args:
        coffee_service_mock (AsyncMock): A mocked CoffeeService.list method.
        test_app (TestApp): An instance of the TestApp class for making test
            requests.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True.
    """
    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.side_effect = HTTPException(
        status_code=404, detail="No coffees found"
    )

    response = await test_app.client.get(
        "/api/v1/coffees",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "No coffees found"}

    coffee_service_mock.assert_awaited_once_with(db_session=get_db_mock)

    app.dependency_overrides = {}
