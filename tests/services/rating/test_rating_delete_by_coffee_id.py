from unittest.mock import AsyncMock

import pytest
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.rating import RatingService
from tests.conftest import DummyRatings


@pytest.mark.asyncio
async def test_rating_service_delete_by_coffee_id(
    dummy_ratings: DummyRatings,
) -> None:
    """
    Test deleting all ratings for a coffee.

    Args:
        dummy_ratings (DummyRatings): A fixture providing dummy rating objects.
    """

    rating_1 = dummy_ratings.rating_1

    rating_crud_mock = AsyncMock()

    db_session_mock = AsyncMock()

    test_rating_service = RatingService(rating_crud=rating_crud_mock)

    await test_rating_service.delete_by_coffee_id(
        db_session=db_session_mock, coffee_id=rating_1.coffee_id
    )
    rating_crud_mock.delete_many.assert_awaited_once_with(
        db_session=db_session_mock, query={"coffee_id": rating_1.coffee_id}
    )


@pytest.mark.asyncio
async def test_rating_service_delete_by_coffee_id_with_unknown_id(
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Ensuring none is returned when no ratings are found for a coffee.

    Args:
        dummy_ratings (DummyRatings): A fixture providing dummy rating objects.
        caplog (pytest.LogCaptureFixture): The log capture fixture.
    """

    unknown_id = uuid7()

    rating_crud_mock = AsyncMock()
    rating_crud_mock.delete_many.side_effect = ObjectNotFoundError(
        "Test message"
    )

    db_session_mock = AsyncMock()

    test_rating_service = RatingService(rating_crud=rating_crud_mock)

    await test_rating_service.delete_by_coffee_id(
        db_session=db_session_mock, coffee_id=unknown_id
    )

    rating_crud_mock.delete_many.assert_awaited_once_with(
        db_session=db_session_mock, query={"coffee_id": unknown_id}
    )
