from uuid import UUID

import pytest
from pydantic import ValidationError

from coffee_backend.schemas import BrewingMethod, CreateRating, Rating


def test_rating_schema_creation() -> None:
    """Test creation of rating schema."""
    rating = Rating(
        _id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        rating=4,
        brewing_method=BrewingMethod.ESPRESSO,
        coffee_id=UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
        user_id=UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
        user_name="test_user",
    )

    assert rating.dict(by_alias=True) == {
        "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        "rating": 4,
        "brewing_method": "Espresso",
        "coffee_id": UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
        "user_id": UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
        "user_name": "test_user",
    }


def test_create_rating_with_invalid_id() -> None:
    """Test creating a Rating instance with an invalid id."""
    with pytest.raises(ValidationError):
        Rating(
            _id="invalid_id",  # type: ignore
            rating=4,
            coffee_id=UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
        )


def test_create_rating_without_id() -> None:
    """Test creating a Rating instance with an invalid id."""
    with pytest.raises(ValidationError):
        Rating(rating=4)  # type: ignore


def test_create_rating_without_rating() -> None:
    """Test creating a Rating instance with an invalid id."""
    with pytest.raises(ValidationError):
        Rating(_id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"))  # type: ignore


def test_create_rating_with_invalid_brewing_method() -> None:
    """Test creating a Rating instance with an invalid brewing method."""
    with pytest.raises(ValidationError):
        Rating(
            _id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
            rating=4,
            brewing_method="Supa Dupa Unknown Brewing Method",  # type: ignore
            coffee_id=UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
            user_id=UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
            user_name="test_user",
        )


def test_create_rating_create_schema() -> None:
    """Test creating a Rating Create schema"""

    create_rating = CreateRating(
        _id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        rating=4,
        brewing_method=BrewingMethod.ESPRESSO,
        coffee_id=UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
    )

    assert create_rating.dict(by_alias=True) == {
        "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        "rating": 4,
        "brewing_method": "Espresso",
        "coffee_id": UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
    }
