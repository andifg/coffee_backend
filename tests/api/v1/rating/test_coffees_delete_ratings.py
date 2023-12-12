from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from uuid_extensions.uuid7 import uuid7

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyCoffees, DummyRatings, TestApp


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@patch("coffee_backend.services.rating.RatingService.delete_rating")
@pytest.mark.asyncio
async def test_api_delete_rating_by_id(
    rating_service_mock: AsyncMock,
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_ratings: DummyRatings,
    mock_security_dependency: Generator,
) -> None:
    """
    Test deleting a rating by ID.

    Args:
        rating_service_mock (AsyncMock): The mocked RatingService.
        test_app (TestApp): The test application.
        dummy_rating (DummyRatings): The dummy ratings fixture.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True
    """
    rating_1 = dummy_ratings.rating_1

    get_db_mock = AsyncMock()

    coffee_service_mock.return_value = "Return without error"
    rating_service_mock.return_value = "Return without error"

    app.dependency_overrides[get_db] = lambda: get_db_mock

    response = await test_app.client.delete(
        f"/api/v1/coffees/{rating_1.coffee_id}/ratings/{rating_1.id}",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.text == ""

    rating_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, rating_id=rating_1.id
    )

    app.dependency_overrides = {}


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@pytest.mark.asyncio
async def test_api_delete_rating_by_id_with_unkown_coffee_id(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    mock_security_dependency: Generator,
) -> None:
    """
    Test deleting a rating by ID for an unknown coffee id.

    Args:
        coffee_service_mock (AsyncMock): The mocked RatingService.
        test_app (TestApp): The test application.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True
    """
    unkown_coffee_id = uuid7()

    unknown_rating_id = uuid7()

    get_db_mock = AsyncMock()

    coffee_service_mock.side_effect = HTTPException(
        status_code=404, detail="No coffee found for given id"
    )

    app.dependency_overrides[get_db] = lambda: get_db_mock

    response = await test_app.client.delete(
        f"/api/v1/coffees/{unkown_coffee_id}/ratings/{unknown_rating_id}",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "No coffee found for given id"}

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=unkown_coffee_id
    )

    app.dependency_overrides = {}
