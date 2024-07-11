from typing import Generator
from unittest.mock import AsyncMock, patch
from uuid import UUID

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
        jsonable_encoder(dummy_ratings.rating_1.model_dump(by_alias=True)),
        jsonable_encoder(dummy_ratings.rating_2.model_dump(by_alias=True)),
    ]

    rating_service_mock.assert_awaited_once_with(
        db_session=get_db_mock,
        coffee_id=None,
        page=1,
        page_size=5,
        first_rating_id=None,
    )

    app.dependency_overrides = {}


@patch("coffee_backend.services.rating.RatingService.list")
@pytest.mark.asyncio
async def test_api_get_ratings_with_query_params(
    rating_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_ratings: DummyRatings,
    mock_security_dependency: Generator,
) -> None:
    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    rating_service_mock.return_value = [
        dummy_ratings.rating_1,
        dummy_ratings.rating_2,
    ]

    response = await test_app.client.get(
        "/api/v1/ratings?coffee_id=0668fdc6-cf0d-7855-8000-24d389e2cbb7&page=1&page_size=5&first_rating_id=0668fdc7-5d12-7ddb-8000-53ff75679f05",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == [
        jsonable_encoder(dummy_ratings.rating_1.model_dump(by_alias=True)),
        jsonable_encoder(dummy_ratings.rating_2.model_dump(by_alias=True)),
    ]

    rating_service_mock.assert_awaited_once_with(
        db_session=get_db_mock,
        coffee_id=UUID("0668fdc6-cf0d-7855-8000-24d389e2cbb7"),
        page=1,
        page_size=5,
        first_rating_id=UUID("0668fdc7-5d12-7ddb-8000-53ff75679f05"),
    )

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

    rating_service_mock.assert_awaited_once_with(
        db_session=get_db_mock,
        coffee_id=None,
        page_size=5,
        page=1,
        first_rating_id=None,
    )

    app.dependency_overrides = {}
