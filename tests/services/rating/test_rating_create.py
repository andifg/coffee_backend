from unittest.mock import AsyncMock

import pytest

from coffee_backend.services.rating import RatingService
from tests.conftest import DummyRatings


@pytest.mark.asyncio
async def test_rating_service_create(
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the create service method with a new rating.

    This test verifies the behavior of the add_coffee method in the
    CoffeeService class when adding a new coffee object that does not already
    exist in the database.

    Args:
        dummy_ratings (DummyRatings): A fixture providing dummy rating objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """
    rating_1 = dummy_ratings.rating_1

    rating_crud_mock = AsyncMock()
    rating_crud_mock.create.return_value = rating_1

    db_session_mock = AsyncMock()

    test_coffee_service = RatingService(rating_crud=rating_crud_mock)

    result = await test_coffee_service.add_rating(
        rating=rating_1, db_session=db_session_mock
    )
    rating_crud_mock.create.assert_awaited_once_with(
        db_session=db_session_mock, rating=rating_1
    )

    assert result == rating_1
