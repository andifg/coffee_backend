from uuid import UUID

import pytest
from pydantic import ValidationError

from coffee_backend.schemas.coffee import Coffee
from coffee_backend.schemas.rating import Rating


def test_coffee_creation_without_ratings() -> None:
    """Test coffee schema creation without any ratings."""
    coffee_id = UUID("123e4567-e89b-12d3-a456-426655440000")
    coffee_name = "Decaf"

    coffee = Coffee(_id=coffee_id, name=coffee_name, ratings=[])

    assert coffee.dict(by_alias=True) == {
        "_id": UUID("123e4567-e89b-12d3-a456-426655440000"),
        "name": "Decaf",
        "ratings": [],
    }


def test_coffee_creation_with_ratings() -> None:
    """Test coffee schema creation with ratings."""
    coffee_id = UUID("123e4567-e89b-12d3-a456-426655440000")
    coffee_name = "Colombian"
    coffee_ratings = [
        Rating(_id=UUID("123e4367-e89b-12d3-a456-426655440000"), rating=4),
        Rating(_id=UUID("123e4367-e49b-12d3-a456-426655440000"), rating=2),
        Rating(_id=UUID("123e4367-e29b-12d3-a456-426655440000"), rating=3),
    ]
    coffee = Coffee(_id=coffee_id, name=coffee_name, ratings=coffee_ratings)

    assert coffee.dict(by_alias=True) == {
        "_id": UUID("123e4567-e89b-12d3-a456-426655440000"),
        "name": "Colombian",
        "ratings": [
            {"_id": UUID("123e4367-e89b-12d3-a456-426655440000"), "rating": 4},
            {"_id": UUID("123e4367-e49b-12d3-a456-426655440000"), "rating": 2},
            {"_id": UUID("123e4367-e29b-12d3-a456-426655440000"), "rating": 3},
        ],
    }


def test_create_coffee_with_invalid_rating() -> None:
    """Test creation ob coffee with invalid ID."""
    # pylint: disable=C0301
    with pytest.raises(ValidationError):
        coffee_id = 1  # invalid rating
        coffee_name = "Colombian"
        coffee_ratings = [
            Rating(_id=UUID("123e4367-e89b-12d3-a456-426655440000"), rating=4),
            Rating(_id=UUID("123e4367-e49b-12d3-a456-426655440000"), rating=2),
            Rating(_id=UUID("123e4367-e29b-12d3-a456-426655440000"), rating=3),
        ]
        Coffee(_id=coffee_id, name=coffee_name, ratings=coffee_ratings)  # type: ignore
