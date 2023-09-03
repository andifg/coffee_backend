from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyCoffees, TestApp


@patch("coffee_backend.services.coffee.CoffeeService.list_ids")
@pytest.mark.asyncio
async def test_api_get_coffees_ids(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_coffees: DummyCoffees,
) -> None:
    """Test the API endpoint for retrieving coffee ids.

    This test ensures that the API endpoint for retrieving coffee ids properly
    handles service layer responses.

    Args:
        coffee_service_mock (AsyncMock): The mocked CoffeeService list_ids
            method.
        test_app (TestApp): The TestApp instance for testing the FastAPI
            application.
        dummy_coffees (DummyCoffees): The dummy coffees fixture.

    Returns:
        None

    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.return_value = [
        dummy_coffees.coffee_1.dict(by_alias=True).get("_id"),
        dummy_coffees.coffee_2.dict(by_alias=True).get("_id"),
    ]

    response = await test_app.client.get(
        "/api/v1/coffees/ids",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == jsonable_encoder(
        [
            dummy_coffees.coffee_1.dict(by_alias=True).get("_id"),
            dummy_coffees.coffee_2.dict(by_alias=True).get("_id"),
        ]
    )

    coffee_service_mock.assert_awaited_once_with(db_session=get_db_mock)

    app.dependency_overrides = {}


@patch("coffee_backend.services.coffee.CoffeeService.list_ids")
@pytest.mark.asyncio
async def test_api_get_coffees_ids_empty_db_collection(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
) -> None:
    """Ensure proper error transformation of service layer error

    Args:
        coffee_service_mock (AsyncMock): The mocked CoffeeService get_by_id
            method.
        test_app (TestApp): The TestApp instance for testing the FastAPI
            application.
    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.side_effect = HTTPException(
        status_code=404, detail="No ids found"
    )

    response = await test_app.client.get(
        "/api/v1/coffees/ids",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "No ids found"}

    coffee_service_mock.assert_awaited_once_with(db_session=get_db_mock)

    app.dependency_overrides = {}
