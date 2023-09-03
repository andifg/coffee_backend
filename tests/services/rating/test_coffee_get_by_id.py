from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.rating import RatingService
from tests.conftest import DummyRatings


@pytest.mark.asyncio
async def test_rating_service_get_by_id(
    dummy_ratings: DummyRatings,
) -> None:
    """Test the get_by_id rating service method

    Args:
        dummy_ratings (DummyRatings): A fixture providing dummy rating objects.
    """
    rating_1 = dummy_ratings.rating_1

    rating_crud_mock = AsyncMock()
    rating_crud_mock.read.return_value = [rating_1]

    db_session_mock = AsyncMock()

    test_rating_service = RatingService(rating_crud=rating_crud_mock)

    result = await test_rating_service.get_by_id(
        db_session=db_session_mock, rating_id=rating_1.id
    )
    rating_crud_mock.read.assert_awaited_once_with(
        db_session=db_session_mock, query={"_id": rating_1.id}
    )

    assert result == rating_1


@pytest.mark.asyncio
async def test_coffee_service_get_by_id_with_unknown_id(
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the list service method.

    Args:
        dummy_ratings (DummyRatings): A fixture providing dummy rating objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """
    unknown_id = uuid7()

    rating_crud_mock = AsyncMock()
    rating_crud_mock.read.side_effect = ObjectNotFoundError("Test message")

    db_session_mock = AsyncMock()

    test_rating_service = RatingService(rating_crud=rating_crud_mock)

    with pytest.raises(HTTPException) as http_error:
        await test_rating_service.get_by_id(
            db_session=db_session_mock, rating_id=unknown_id
        )

    assert str(http_error.value.detail) == "No rating found for given id"
