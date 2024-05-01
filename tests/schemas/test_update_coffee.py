from uuid import UUID

import pytest
from pydantic import ValidationError
from uuid_extensions.uuid7 import uuid7

from coffee_backend.schemas.coffee import UpdateCoffee


def test_update_coffee_creation_without_ratings() -> None:
    """Test coffee schema creation without any ratings."""
    coffee_name = "Decaf"

    coffee = UpdateCoffee(
        name=coffee_name,
        owner_id=UUID("018ee105-66b3-7f89-b6f3-807782e40350"),
        owner_name="Jdoe",
    )

    assert coffee.dict(by_alias=True) == {
        "name": "Decaf",
        "owner_id": UUID("018ee105-66b3-7f89-b6f3-807782e40350"),
        "owner_name": "Jdoe",
    }


def test_create_update_coffee_with_invalid_attribute() -> None:
    """Test creation ob coffee with invalid ID."""
    # pylint: disable=C0301
    with pytest.raises(ValidationError):
        coffee_id = uuid7()  # invalid attribute
        coffee_name = "Colombian"
        UpdateCoffee(_id=coffee_id, name=coffee_name)  # type: ignore
    # pylint: enable=C0301
