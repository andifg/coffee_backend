from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.rating import RatingService
from tests.conftest import DummyRatings


@pytest.mark.asyncio
async def test_rating_service_read(
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the list service method.

    Args:
        dummy_ratings (DummyRatings): A fixture providing dummy rating objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """
    rating_1 = dummy_ratings.rating_1
    rating_2 = dummy_ratings.rating_2

    coffee_crud_mock = AsyncMock()
    coffee_crud_mock.read.return_value = [rating_1, rating_2]

    db_session_mock = AsyncMock()

    test_rating_service = RatingService(rating_crud=coffee_crud_mock)

    result = await test_rating_service.list(
        db_session=db_session_mock,
    )
    coffee_crud_mock.read.assert_awaited_once_with(
        db_session=db_session_mock, query={}
    )

    assert result == [rating_1, rating_2]


@pytest.mark.asyncio
async def test_rating_service_read_with_empty_db_coffee_collection(
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the list service method to return an emtpy error if no ratings
        are found.

    Args:
        dummy_ratings (DummyRatings): A fixture providing dummy coffee objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """

    rating_crud_mock = AsyncMock()
    rating_crud_mock.read.side_effect = ObjectNotFoundError("Test message")

    db_session_mock = AsyncMock()

    test_rating_service = RatingService(rating_crud=rating_crud_mock)

    result = await test_rating_service.list(
        db_session=db_session_mock,
    )

    assert result == []
