from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from uuid_extensions.uuid7 import uuid7

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyCoffees, TestApp


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@pytest.mark.asyncio
async def test_api_get_coffee_by_id(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_coffees: DummyCoffees,
) -> None:
    """Test the API endpoint for retrieving a coffee by ID.

    This test ensures that the API endpoint for retrieving a coffee by ID
    returns the expected response.

    Args:
        coffee_service_mock (AsyncMock): The mocked CoffeeService get_by_id
            method.
        test_app (TestApp): The TestApp instance for testing the FastAPI
            application.
        dummy_coffees (DummyCoffees): The dummy coffees fixture.
    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.return_value = dummy_coffees.coffee_1.dict(
        by_alias=True
    )

    response = await test_app.client.get(
        f"/api/v1/coffees/{dummy_coffees.coffee_1.id}",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == jsonable_encoder(
        dummy_coffees.coffee_1.dict(by_alias=True)
    )

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=dummy_coffees.coffee_1.id
    )

    app.dependency_overrides = {}


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@pytest.mark.asyncio
async def test_api_get_coffee_by_id_with_unkown_id(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
) -> None:
    """Ensure proper error transformation of service layer error


    Args:
        coffee_service_mock (AsyncMock): The mocked CoffeeService get_by_id
            method.
        test_app (TestApp): The TestApp instance for testing the FastAPI
            application.
        dummy_coffees (DummyCoffees): The dummy coffees fixture.

    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.side_effect = HTTPException(
        status_code=404, detail="No coffee found for given id"
    )

    unkown_id = uuid7()

    response = await test_app.client.get(
        f"/api/v1/coffees/{unkown_id}",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "No coffee found for given id"}

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=unkown_id
    )

    app.dependency_overrides = {}
