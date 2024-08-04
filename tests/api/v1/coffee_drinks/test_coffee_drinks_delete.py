from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from uuid_extensions.uuid7 import uuid7

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyCoffees, DummyRatings, TestApp


@patch("coffee_backend.services.rating.RatingService.delete_rating")
@pytest.mark.asyncio
async def test_api_delete_coffee_drink_by_id(
    rating_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_ratings: DummyRatings,
    mock_security_dependency: Generator,
) -> None:
    """
    Test deleting a coffee_drink by ID.

    Args:
        rating_service_mock (AsyncMock): The mocked RatingService.
        test_app (TestApp): The test application.
        dummy_rating (DummyRatings): The dummy ratings fixture.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True
    """
    rating_1 = dummy_ratings.rating_1

    get_db_mock = AsyncMock()

    rating_service_mock.return_value = "Return without error"

    app.dependency_overrides[get_db] = lambda: get_db_mock

    response = await test_app.client.delete(
        f"/api/v1/coffee_drinks/{rating_1.id}",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.text == ""

    rating_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, rating_id=rating_1.id
    )

    app.dependency_overrides = {}
