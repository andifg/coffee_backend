from uuid import UUID

import pytest
from pydantic import ValidationError

from coffee_backend.schemas.rating import Rating


def test_rating_schema_creation() -> None:
    """Test creation of rating schema."""
    rating = Rating(
        _id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        rating=4,
        coffee_id=UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
    )

    assert rating.dict(by_alias=True) == {
        "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        "rating": 4,
        "coffee_id": UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
    }


def test_create_rating_with_invalid_id() -> None:
    """Test creating a Rating instance with an invalid id."""
    with pytest.raises(ValidationError):
        Rating(_id="invalid_id", rating=4, coffee_id=UUID("c9ba633e-c38c-11ed-afb4-acde48001122"))  # type: ignore


def test_create_rating_without_id() -> None:
    """Test creating a Rating instance with an invalid id."""
    with pytest.raises(ValidationError):
        Rating(rating=4)  # type: ignore


def test_create_rating_without_rating() -> None:
    """Test creating a Rating instance with an invalid id."""
    with pytest.raises(ValidationError):
        Rating(_id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"))  # type: ignore
