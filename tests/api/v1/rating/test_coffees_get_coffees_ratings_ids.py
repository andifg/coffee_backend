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
@patch("coffee_backend.services.rating.RatingService.list_ids_for_coffee")
@pytest.mark.asyncio
async def test_api_get_coffees_ratings_ids(
    rating_service_mock: AsyncMock,
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_ratings: DummyRatings,
    mock_security_dependency: Generator,
) -> None:
    """Test coffees ratings ids endpoint get method."""

    rating_1 = dummy_ratings.rating_1
    rating_2 = dummy_ratings.rating_2

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    rating_service_mock.return_value = [
        rating_1.id,
        rating_2.id,
    ]

    coffee_service_mock.return_value = "test"

    response = await test_app.client.get(
        f"/api/v1/coffees/{rating_1.id}/rating-ids",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == [str(rating_1.id), str(rating_2.id)]

    rating_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=rating_1.id
    )

    app.dependency_overrides = {}


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@patch("coffee_backend.services.rating.RatingService.list_ids_for_coffee")
@pytest.mark.asyncio
async def test_api_get_coffees_ratings_ids_for_non_existing_coffee(
    rating_service_mock: AsyncMock,
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    mock_security_dependency: Generator,
) -> None:
    """Test coffees ratings ids endpoint get method with non existing
    coffee id.

    Args:
        rating_service_mock (AsyncMock): The mocked RatingService.
        coffee_service_mock (AsyncMock): The mocked CoffeeService.
        test_app (TestApp): The test application.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True.
    """

    unknown_coffee_id = uuid7()

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.side_effect = HTTPException(
        status_code=404, detail="No coffee found for given id"
    )

    response = await test_app.client.get(
        f"/api/v1/coffees/{unknown_coffee_id}/rating-ids",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404

    assert response.json() == {"detail": "No coffee found for given id"}

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=unknown_coffee_id
    )

    assert rating_service_mock.await_count == 0

    app.dependency_overrides = {}


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@patch("coffee_backend.services.rating.RatingService.list_ids_for_coffee")
@pytest.mark.asyncio
async def test_api_get_coffees_ratings_ids_coffee_without_ratings(
    rating_service_mock: AsyncMock,
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    mock_security_dependency: Generator,
) -> None:
    """Test coffees ratings ids endpoint get method for coffee without
    ratings.

    Args:
        rating_service_mock (AsyncMock): The mocked RatingService.
        coffee_service_mock (AsyncMock): The mocked CoffeeService.
        test_app (TestApp): The test application.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True.
    """

    coffee_id = uuid7()

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.return_value = "test"

    rating_service_mock.return_value = []

    response = await test_app.client.get(
        f"/api/v1/coffees/{coffee_id}/rating-ids",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200

    assert response.json() == []

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=coffee_id
    )

    rating_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=coffee_id
    )

    app.dependency_overrides = {}
