from uuid import UUID

import pytest
from pydantic import ValidationError

from coffee_backend.schemas import BrewingMethod, CreateDrink, Drink


def test_drink_schema_creation_with_coffee_bean_and_image() -> None:
    """Test creation of drink schema."""
    drink = Drink(
        _id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        rating=4,
        brewing_method=BrewingMethod.ESPRESSO,
        coffee_bean_id=UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
        user_id=UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
        user_name="test_user",
        image_exists=True,
    )

    assert drink.model_dump(by_alias=True) == {
        "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        "rating": 4,
        "brewing_method": "Espresso",
        "coffee_bean_id": UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
        "user_id": UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
        "user_name": "test_user",
        "image_exists": True,
    }


def test_drink_schema_creation_without_coffee_bean_data() -> None:
    """Test creation of drink schema."""
    drink = Drink(
        _id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        rating=4,
        user_id=UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
        user_name="test_user",
        image_exists=True,
    )

    assert drink.model_dump(by_alias=True) == {
        "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        "rating": 4,
        "brewing_method": None,
        "coffee_bean_id": None,
        "user_id": UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
        "user_name": "test_user",
        "image_exists": True,
    }


def test_create_drink_without_id() -> None:
    """Test creating a Drink instance with an invalid id."""
    with pytest.raises(ValidationError):
        Drink(rating=4)  # type: ignore


def test_create_drink_without_rating() -> None:
    """Test creating a Drink instance with an invalid id."""
    with pytest.raises(ValidationError):
        Drink(_id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"))  # type: ignore


def test_create_drink_with_invalid_brewing_method() -> None:
    """Test creating a Drink instance with an invalid brewing method."""
    with pytest.raises(ValidationError):
        Drink(
            _id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
            rating=4,
            brewing_method="Supa Dupa Unknown Brewing Method",  # type: ignore
            coffee_bean_id=UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
            user_id=UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
            user_name="test_user",
        )


def test_create_drink_create_schema() -> None:
    """Test creating a Drink Create schema"""

    create_drink = CreateDrink(
        _id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        rating=4,
        brewing_method=BrewingMethod.ESPRESSO,
        coffee_bean_id=UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
        image_exists=False,
    )

    assert create_drink.model_dump(by_alias=True) == {
        "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        "rating": 4,
        "brewing_method": "Espresso",
        "coffee_bean_id": UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
        "image_exists": False,
    }


def test_create_drink_create_schema_minimal() -> None:
    """Test creating a Drink Create schema with minimal data."""

    create_drink = CreateDrink(
        _id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        rating=4,
    )

    assert create_drink.model_dump(by_alias=True) == {
        "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        "rating": 4,
        "brewing_method": None,
        "coffee_bean_id": None,
        "image_exists": False,
    }
