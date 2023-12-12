from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyCoffees, DummyRatings, TestApp


@patch("coffee_backend.services.rating.RatingService.list")
@pytest.mark.asyncio
async def test_api_get_ratings(
    rating_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_ratings: DummyRatings,
    mock_security_dependency: Generator,
) -> None:
    """Test the API endpoint to retrieve a list of ratings.

    Args:
        rating_service_mock (AsyncMock): An asynchronous mock object for the
            RatingService.
        test_app (TestApp): An instance of the TestApp for testing.
        dummy_ratings (DummyRatings): A fixture providing dummy rating data.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True.
    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    rating_service_mock.return_value = [
        dummy_ratings.rating_1,
        dummy_ratings.rating_2,
    ]

    response = await test_app.client.get(
        "/api/v1/ratings",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == [
        jsonable_encoder(dummy_ratings.rating_1.dict(by_alias=True)),
        jsonable_encoder(dummy_ratings.rating_2.dict(by_alias=True)),
    ]

    rating_service_mock.assert_awaited_once_with(db_session=get_db_mock)

    app.dependency_overrides = {}


@patch("coffee_backend.services.rating.RatingService.list")
@pytest.mark.asyncio
async def test_api_get_ratings_with_emtpy_crud_response(
    rating_service_mock: AsyncMock,
    test_app: TestApp,
    mock_security_dependency: Generator,
) -> None:
    """Test the rating 'get ratings' endpoint with an empty rating database
        collection.

    Args:
        rating_service_mock (AsyncMock): A mocked RatingService.list method.
        test_app (TestApp): An instance of the TestApp class for making test
            requests.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True
    """
    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    rating_service_mock.return_value = []

    response = await test_app.client.get(
        "/api/v1/ratings",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == []

    rating_service_mock.assert_awaited_once_with(db_session=get_db_mock)

    app.dependency_overrides = {}
