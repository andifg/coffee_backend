from unittest.mock import AsyncMock

import pytest
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.rating import RatingService
from tests.conftest import DummyRatings


@pytest.mark.asyncio
async def test_rating_service_list_ids_for_coffee(
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the list ids coffee service method

    Args:
        dummy_ratings (DummyRatings): A fixture providing dummy rating objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """
    rating_1 = dummy_ratings.rating_1
    rating_2 = dummy_ratings.rating_2

    rating_crud_mock = AsyncMock()
    rating_crud_mock.read.return_value = [rating_1, rating_2]

    db_session_mock = AsyncMock()

    coffee_uuid = uuid7()

    test_rating_service = RatingService(rating_crud=rating_crud_mock)

    result = await test_rating_service.list_ids_for_coffee(
        db_session=db_session_mock, coffee_id=coffee_uuid
    )
    rating_crud_mock.read.assert_awaited_once_with(
        db_session=db_session_mock,
        query={"coffee_id": coffee_uuid},
        projection={},
    )

    assert result == [rating_1.id, rating_2.id]


@pytest.mark.asyncio
async def test_rating_service_list_ids_for_coffee_with_empty_db(
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the list service method to return empty list.

    Args:
        dummy_ratings (DummyRatings): A fixture providing dummy rating objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """

    rating_crud_mock = AsyncMock()
    rating_crud_mock.read.side_effect = ObjectNotFoundError("Test message")

    db_session_mock = AsyncMock()

    test_rating_service = RatingService(rating_crud=rating_crud_mock)

    result = await test_rating_service.list_ids_for_coffee(
        db_session=db_session_mock, coffee_id=uuid7()
    )

    assert result == []
