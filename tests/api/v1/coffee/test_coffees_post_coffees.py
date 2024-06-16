from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.encoders import jsonable_encoder

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas.coffee import CreateCoffee
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

    coffee_service_mock.return_value = dummy_coffees.coffee_1.model_dump(
        by_alias=True
    )

    create_coffee = CreateCoffee(
        _id=dummy_coffees.coffee_1.id,
        name=dummy_coffees.coffee_1.name,
        roasting_company=dummy_coffees.coffee_1.roasting_company,
    )

    create_coffee_jsonable = jsonable_encoder(
        create_coffee.model_dump(by_alias=True)
    )

    response = await test_app.client.post(
        "/api/v1/coffees/",
        json=create_coffee_jsonable,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 201
    assert response.json() == jsonable_encoder(
        dummy_coffees.coffee_1.model_dump(by_alias=True)
    )

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
    """Test coffees endpoint post mehtod with invalid coffee. Ensures that the
    endpoint can only be used with create coffee schema.

    Args:
        test_app (TestApp): An instance of the TestApp class for making test
            requests.
        dummy_coffees (DummyCoffees): The dummy coffees fixture.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True.


    """

    coffee = dummy_coffees.coffee_1

    del coffee.id

    coffee_jsonable = jsonable_encoder(coffee.model_dump(by_alias=True))

    response = await test_app.client.post(
        "/api/v1/coffees/",
        json=coffee_jsonable,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "_id"],
                "msg": "Field required",
                "input": {
                    "name": "Colombian",
                    "roasting_company": "Starbucks",
                    "owner_id": "018ee105-66b3-7f89-b6f3-807782e40350",
                    "owner_name": "Jdoe",
                    "rating_count": None,
                    "rating_average": None,
                },
            },
            {
                "type": "extra_forbidden",
                "loc": ["body", "owner_id"],
                "msg": "Extra inputs are not permitted",
                "input": "018ee105-66b3-7f89-b6f3-807782e40350",
            },
            {
                "type": "extra_forbidden",
                "loc": ["body", "owner_name"],
                "msg": "Extra inputs are not permitted",
                "input": "Jdoe",
            },
            {
                "type": "extra_forbidden",
                "loc": ["body", "rating_count"],
                "msg": "Extra inputs are not permitted",
                "input": None,
            },
            {
                "type": "extra_forbidden",
                "loc": ["body", "rating_average"],
                "msg": "Extra inputs are not permitted",
                "input": None,
            },
        ]
    }
