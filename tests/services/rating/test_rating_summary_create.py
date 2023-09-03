from copy import deepcopy
from unittest.mock import AsyncMock

import pytest
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.schemas.rating_summary import RatingSummary
from coffee_backend.services.rating import RatingService
from tests.conftest import DummyRatings


@pytest.mark.asyncio
async def test_rating_service_rating_summary_create(
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test creation of a rating summary for a coffee.

    This test verifies the behavior of the create rating summary method in the
    RatingService class.

    Args:
        dummy_ratings (DummyRatings): A fixture providing dummy rating objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """

    coffee_id = uuid7()

    rating_1 = dummy_ratings.rating_1
    rating_2 = dummy_ratings.rating_2
    rating_3 = deepcopy(dummy_ratings.rating_2)
    rating_4 = deepcopy(dummy_ratings.rating_1)

    rating_crud_mock = AsyncMock()
    rating_crud_mock.read.return_value = [
        rating_1,
        rating_2,
        rating_3,
        rating_4,
    ]

    db_session_mock = AsyncMock()

    test_rating_service = RatingService(rating_crud=rating_crud_mock)

    result = await test_rating_service.create_rating_summary_for_coffee(
        coffee_id=coffee_id, db_session=db_session_mock
    )
    rating_crud_mock.read.assert_awaited_once_with(
        db_session=db_session_mock,
        query={"coffee_id": coffee_id},
        projection={},
    )

    assert result == RatingSummary(
        coffee_id=coffee_id, rating_count=4, rating_average=4.75
    )


@pytest.mark.asyncio
async def test_rating_service_rating_summary_create_with_empty_ratings(
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test creation of a rating summary for a coffee with no ratings.

    This test verifies the behavior of the create rating summary method in the
    RatingService class when there are no ratings for the coffee.

    Args:
        dummy_ratings (DummyRatings): A fixture providing dummy rating objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """

    coffee_id = uuid7()

    rating_crud_mock = AsyncMock()
    rating_crud_mock.read.side_effect = ObjectNotFoundError("Test message")

    db_session_mock = AsyncMock()

    test_rating_service = RatingService(rating_crud=rating_crud_mock)

    result = await test_rating_service.create_rating_summary_for_coffee(
        coffee_id=coffee_id, db_session=db_session_mock
    )
    rating_crud_mock.read.assert_awaited_once_with(
        db_session=db_session_mock,
        query={"coffee_id": coffee_id},
        projection={},
    )

    assert result == RatingSummary(
        coffee_id=coffee_id, rating_count=0, rating_average=0
    )
