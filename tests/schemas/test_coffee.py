from uuid import UUID

import pytest
from pydantic import ValidationError

from coffee_backend.schemas.coffee import Coffee


def test_coffee_creation_without_ratings() -> None:
    """Test coffee schema creation without any ratings."""
    coffee_id = UUID("123e4567-e89b-12d3-a456-426655440000")
    coffee_name = "Decaf"
    roasting_company = "Starbucks"
    owner_id = UUID("018ee105-66b3-7f89-b6f3-807782e40350")
    owner_name = "Jdoe"

    coffee = Coffee(
        _id=coffee_id,
        name=coffee_name,
        roasting_company=roasting_company,
        owner_id=owner_id,
        owner_name=owner_name,
    )

    assert coffee.model_dump(by_alias=True) == {
        "_id": UUID("123e4567-e89b-12d3-a456-426655440000"),
        "name": "Decaf",
        "roasting_company": "Starbucks",
        "owner_id": UUID("018ee105-66b3-7f89-b6f3-807782e40350"),
        "owner_name": "Jdoe",
        "rating_count": None,
        "rating_average": None,
    }


def test_create_coffee_with_rating_summary() -> None:
    """Create a coffee with rating summary."""

    coffee_id = UUID("123e4567-e89b-12d3-a456-426655440000")
    coffee_name = "Decaf"
    roasting_company = "Starbucks"
    owner_id = UUID("018ee105-66b3-7f89-b6f3-807782e40350")
    owner_name = "Jdoe"

    coffee = Coffee(
        _id=coffee_id,
        name=coffee_name,
        roasting_company=roasting_company,
        owner_id=owner_id,
        owner_name=owner_name,
        rating_count=0,
        rating_average=0,
    )

    assert coffee.model_dump(by_alias=True) == {
        "_id": UUID("123e4567-e89b-12d3-a456-426655440000"),
        "name": "Decaf",
        "roasting_company": "Starbucks",
        "owner_id": UUID("018ee105-66b3-7f89-b6f3-807782e40350"),
        "owner_name": "Jdoe",
        "rating_count": 0,
        "rating_average": 0.0,
    }


def test_create_coffee_with_invalid_rating() -> None:
    """Test creation ob coffee with invalid ID."""
    # pylint: disable=C0301
    with pytest.raises(ValidationError):
        coffee_id = 1  # invalid rating
        coffee_name = "Colombian"
        Coffee(_id=coffee_id, name=coffee_name)  # type: ignore
    # pylint: enable=C0301
