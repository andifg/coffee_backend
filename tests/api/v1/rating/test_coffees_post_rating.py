from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas import CreateRating
from tests.conftest import DummyRatings, TestApp


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@patch("coffee_backend.services.rating.RatingService.add_rating")
@pytest.mark.asyncio
async def test_api_create_rating(
    rating_service_mock: AsyncMock,
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_ratings: DummyRatings,
    mock_security_dependency: Generator,
) -> None:
    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.return_value = {}

    rating_service_mock.return_value = dummy_ratings.rating_1.model_dump(
        by_alias=True
    )

    create_rating = CreateRating(
        _id=dummy_ratings.rating_1.id,
        rating=dummy_ratings.rating_1.rating,
        brewing_method=dummy_ratings.rating_1.brewing_method,
        coffee_id=dummy_ratings.rating_1.coffee_id,
        image_exists=dummy_ratings.rating_1.image_exists,
    )

    create_coffee_jsonable = jsonable_encoder(
        create_rating.model_dump(by_alias=True)
    )

    response = await test_app.client.post(
        f"/api/v1/coffees/{dummy_ratings.rating_1.coffee_id}/ratings",
        json=create_coffee_jsonable,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 201
    assert response.json() == jsonable_encoder(
        dummy_ratings.rating_1.model_dump(by_alias=True)
    )

    rating_service_mock.assert_awaited_once_with(
        rating=dummy_ratings.rating_1, db_session=get_db_mock
    )

    app.dependency_overrides = {}


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@pytest.mark.asyncio
async def test_api_create_rating_with_not_existing_coffee(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_ratings: DummyRatings,
    mock_security_dependency: Generator,
) -> None:
    coffee_service_mock.side_effect = HTTPException(
        status_code=404, detail="No coffee found for given id"
    )

    create_rating = CreateRating(
        _id=dummy_ratings.rating_1.id,
        rating=dummy_ratings.rating_1.rating,
        brewing_method=dummy_ratings.rating_1.brewing_method,
        coffee_id=dummy_ratings.rating_1.coffee_id,
    )

    create_coffee_jsonable = jsonable_encoder(
        create_rating.model_dump(by_alias=True)
    )

    response = await test_app.client.post(
        f"/api/v1/coffees/{dummy_ratings.rating_1.coffee_id}/ratings",
        json=create_coffee_jsonable,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404
