from uuid import UUID

import pytest
from pydantic import ValidationError

from coffee_backend.schemas.coffee import Coffee


def test_coffee_creation_without_ratings() -> None:
    """Test coffee schema creation without any ratings."""
    coffee_id = UUID("123e4567-e89b-12d3-a456-426655440000")
    coffee_name = "Decaf"

    coffee = Coffee(_id=coffee_id, name=coffee_name)

    assert coffee.dict(by_alias=True) == {
        "_id": UUID("123e4567-e89b-12d3-a456-426655440000"),
        "name": "Decaf",
    }


def test_create_coffee_with_invalid_rating() -> None:
    """Test creation ob coffee with invalid ID."""
    # pylint: disable=C0301
    with pytest.raises(ValidationError):
        coffee_id = 1  # invalid rating
        coffee_name = "Colombian"
        Coffee(_id=coffee_id, name=coffee_name)  # type: ignore
    # pylint: enable=C0301
