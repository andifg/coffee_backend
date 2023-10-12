from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from uuid_extensions.uuid7 import uuid7

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyCoffees, TestApp


@patch("coffee_backend.services.rating.RatingService.delete_by_coffee_id")
@patch("coffee_backend.services.coffee.CoffeeService.delete_coffee")
@pytest.mark.asyncio
async def test_api_delete_coffee_by_id(
    coffee_service_mock: AsyncMock,
    rating_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_coffees: DummyCoffees,
) -> None:
    """
    Test deleting a coffee by ID.

    Args:
        coffee_service_mock (AsyncMock): The mocked CoffeeService.
        rating_service_mock (AsyncMock): The mocked RatingService.
        test_app (TestApp): The test application.
        dummy_coffees (DummyCoffees): The dummy coffees fixture.
    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    response = await test_app.client.delete(
        f"/api/v1/coffees/{dummy_coffees.coffee_1.id}",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.text == ""

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=dummy_coffees.coffee_1.id
    )

    rating_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=dummy_coffees.coffee_1.id
    )

    app.dependency_overrides = {}


@patch("coffee_backend.services.rating.RatingService.delete_by_coffee_id")
@patch("coffee_backend.services.coffee.CoffeeService.delete_coffee")
@pytest.mark.asyncio
async def test_api_delete_coffee_by_id_with_unkown_id(
    coffee_service_mock: AsyncMock,
    rating_service_mock: AsyncMock,
    test_app: TestApp,
) -> None:
    """
    Ensuring error is returned when id is not known.

    Args:
        coffee_service_mock (AsyncMock): The mocked CoffeeService.
        test_app (TestApp): The test application.
    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.side_effect = HTTPException(
        status_code=404, detail="No coffee found for given id"
    )

    unkown_id = uuid7()

    response = await test_app.client.delete(
        f"/api/v1/coffees/{unkown_id}",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "No coffee found for given id"}

    rating_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=unkown_id
    )

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=unkown_id
    )

    app.dependency_overrides = {}
