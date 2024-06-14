from uuid import UUID

import pytest
from pydantic import ValidationError
from uuid_extensions.uuid7 import uuid7

from coffee_backend.schemas.coffee import CreateCoffee


def test_create_coffee_schema_without_ratings() -> None:
    """Test create coffee schema creation without any ratings."""

    coffee = CreateCoffee(
        _id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        name="Decaf",
        roasting_company="Starbucks",
    )

    assert coffee.dict(by_alias=True) == {
        "name": "Decaf",
        "roasting_company": "Starbucks",
        "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
    }


def test_create_coffee_schema_with_invalid_attribute() -> None:
    """Test creation of cerate coffee schema with invalid ID."""
    # pylint: disable=C0301
    with pytest.raises(ValidationError):
        owner_id = uuid7()  # invalid attribute
        coffee_name = "Colombian"
        CreateCoffee(_id=uuid7(), name=coffee_name, owner_id=owner_id)  # type: ignore
    # pylint: enable=C0301
