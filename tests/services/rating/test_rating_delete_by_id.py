from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.rating import RatingService
from tests.conftest import DummyRatings


@pytest.mark.asyncio
async def test_rating_service_delete_by_id(
    dummy_ratings: DummyRatings,
) -> None:
    """
    Test deleting a rating by ID.

    Args:
        dummy_ratings (DummyRatings): A fixture providing dummy rating objects.
    """

    rating_1 = dummy_ratings.rating_1

    rating_crud_mock = AsyncMock()

    db_session_mock = AsyncMock()

    test_rating_service = RatingService(rating_crud=rating_crud_mock)

    await test_rating_service.delete_rating(
        db_session=db_session_mock, rating_id=rating_1.id
    )
    rating_crud_mock.delete.assert_awaited_once_with(
        db_session=db_session_mock, rating_id=rating_1.id
    )


@pytest.mark.asyncio
async def test_rating_service_delete_by_id_with_unknown_id(
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Ensuring HTTP exception is thrown when rating id is not known.

    Args:
        dummy_ratings (DummyRatings): A fixture providing dummy rating objects.
        caplog (pytest.LogCaptureFixture): The log capture fixture.
    """

    unknown_id = uuid7()

    rating_crud_mock = AsyncMock()
    rating_crud_mock.delete.side_effect = ObjectNotFoundError("Test message")

    db_session_mock = AsyncMock()

    test_rating_service = RatingService(rating_crud=rating_crud_mock)

    with pytest.raises(HTTPException) as http_error:
        await test_rating_service.delete_rating(
            db_session=db_session_mock, rating_id=unknown_id
        )

    assert str(http_error.value.detail) == "No rating found for given id"
