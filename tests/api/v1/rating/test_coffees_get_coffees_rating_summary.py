from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from uuid_extensions.uuid7 import uuid7

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas.rating_summary import RatingSummary
from tests.conftest import DummyCoffees, DummyRatings, TestApp


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@patch(
    "coffee_backend.services.rating.RatingService.create_rating_summary_for_coffee"
)
@pytest.mark.asyncio
async def test_api_get_coffees_rating_summary(
    rating_service_mock: AsyncMock,
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_ratings: DummyRatings,
    mock_security_dependency: Generator,
) -> None:
    """Test coffees rating summary get endpoint.

    Args:
        rating_service_mock (AsyncMock): The mocked RatingService.
        test_app (TestApp): The test application.
        dummy_ratings (DummyRatings): The dummy ratings fixture.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True.
    """

    dummy_id = uuid7()

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    rating_summary = RatingSummary(
        coffee_id=dummy_id, rating_average=4.5, rating_count=2
    )

    rating_jsonable = jsonable_encoder(rating_summary.dict(by_alias=True))

    rating_service_mock.return_value = rating_summary

    coffee_service_mock.return_value = "Return without error"

    response = await test_app.client.get(
        f"/api/v1/coffees/{dummy_id}/rating-summary",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == rating_jsonable

    rating_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=dummy_id
    )

    app.dependency_overrides = {}


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@patch(
    "coffee_backend.services.rating.RatingService.create_rating_summary_for_coffee"
)
@pytest.mark.asyncio
async def test_api_get_coffees_rating_summary_for_non_existing_coffee(
    rating_service_mock: AsyncMock,
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_ratings: DummyRatings,
    mock_security_dependency: Generator,
) -> None:
    """Test coffees rating summary get endpoint.

    Args:
        rating_service_mock (AsyncMock): The mocked RatingService.
        coffee_service_mock (AsyncMock): The mocked CoffeeService.
        test_app (TestApp): The test application.
        dummy_ratings (DummyRatings): The dummy ratings fixture.
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
        f"/api/v1/coffees/{unknown_coffee_id}/rating-summary",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "No coffee found for given id"}

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=unknown_coffee_id
    )

    app.dependency_overrides = {}
