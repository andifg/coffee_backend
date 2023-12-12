from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.encoders import jsonable_encoder

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyCoffees, TestApp


@patch("coffee_backend.services.coffee.CoffeeService.add_coffee")
@pytest.mark.asyncio
async def test_api_create_coffee(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_coffees: DummyCoffees,
    mock_security_dependency: Generator,
) -> None:
    """Test coffees endpoint post mehtod with valid coffee.

    Args:
        coffee_service_mock (AsyncMock): A mocked CoffeeService.add_coffee method.
        test_app (TestApp): An instance of the TestApp class for making test
            requests.
        dummy_coffees (DummyCoffees): The dummy coffees fixture.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True.
    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.return_value = dummy_coffees.coffee_1.dict(
        by_alias=True
    )

    coffee = dummy_coffees.coffee_1

    coffee_jsonable = jsonable_encoder(coffee.dict(by_alias=True))

    response = await test_app.client.post(
        "/api/v1/coffees/",
        json=coffee_jsonable,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 201
    assert response.json() == coffee_jsonable

    coffee_service_mock.assert_awaited_once_with(
        coffee=dummy_coffees.coffee_1, db_session=get_db_mock
    )

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_api_create_invalid_coffee(
    test_app: TestApp,
    dummy_coffees: DummyCoffees,
    mock_security_dependency: Generator,
) -> None:
    """Test coffees endpoint post mehtod with invalid coffee.

    Args:
        test_app (TestApp): An instance of the TestApp class for making test
            requests.
        dummy_coffees (DummyCoffees): The dummy coffees fixture.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True.


    """

    coffee = dummy_coffees.coffee_1

    del coffee.id

    coffee_jsonable = jsonable_encoder(coffee.dict(by_alias=True))

    response = await test_app.client.post(
        "/api/v1/coffees/",
        json=coffee_jsonable,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "_id"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }
