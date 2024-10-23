from typing import Any, Dict, Type
from uuid import UUID

import pytest
from pydantic import ValidationError
from pydantic_extra_types.coordinate import Coordinate

from coffee_backend.schemas import CreateDrink, Drink


@pytest.mark.parametrize(
    "input_object,expected_dict",
    [
        (
            {
                "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
                "rating": 4,
                "brewing_method": "Espresso",
                "coffee_bean_id": UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
                "user_id": UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
                "user_name": "test_user",
                "image_exists": True,
                "coffee_bean_name": "test_coffee_bean",
                "coffee_bean_roasting_company": "test_roasting_company",
                "coordinate": Coordinate(latitude=1, longitude=1),
            },
            {
                "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
                "rating": 4,
                "brewing_method": "Espresso",
                "coffee_bean_id": UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
                "user_id": UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
                "user_name": "test_user",
                "image_exists": True,
                "coffee_bean_name": "test_coffee_bean",
                "coffee_bean_roasting_company": "test_roasting_company",
                "coordinate": {"latitude": 1.0, "longitude": 1.0},
            },
        ),
        (
            {
                "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
                "rating": 4,
                "brewing_method": "Espresso",
                "coffee_bean_id": UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
                "user_id": UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
                "user_name": "test_user",
                "coffee_bean_name": "test_coffee_bean",
                "coffee_bean_roasting_company": "test_roasting_company",
            },
            {
                "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
                "rating": 4,
                "brewing_method": "Espresso",
                "coffee_bean_id": UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
                "user_id": UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
                "user_name": "test_user",
                "image_exists": False,
                "coffee_bean_name": "test_coffee_bean",
                "coffee_bean_roasting_company": "test_roasting_company",
                "coordinate": None,
            },
        ),
    ],
)
def test_drink_schema_creation_success(
    input_object: Dict[str, Any], expected_dict: object
) -> None:
    """Test successful creation of drink schema."""
    drink = Drink(**input_object)
    assert drink.model_dump(by_alias=True) == expected_dict


@pytest.mark.parametrize(
    "input_object,expected_exception",
    [
        (
            {
                "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
            },
            ValueError,
        ),
        (
            {
                "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
                "rating": 4,
                "brewing_method": "Supa Dupa Unknown Brewing Method",
                "coffee_bean_id": UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
                "user_id": UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
                "user_name": "test_user",
                "coffee_bean_name": "test_coffee_bean",
                "coffee_bean_roasting_company": "test_roasting_company",
            },
            ValidationError,
        ),
        (
            {"_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122")},
            ValidationError,
        ),
    ],
)
def test_drink_schema_creation_failure(
    input_object: Dict[str, Any], expected_exception: Type[BaseException]
) -> None:
    """Test creation failure of drink schema."""
    with pytest.raises(expected_exception):
        Drink(**input_object)


@pytest.mark.parametrize(
    "input_object,expected_dict",
    [
        (
            {
                "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
                "rating": 4,
                "brewing_method": "Espresso",
                "coffee_bean_id": UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
                "image_exists": True,
                "coordinate": {"latitude": 1.0, "longitude": 1.0},
            },
            {
                "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
                "rating": 4,
                "brewing_method": "Espresso",
                "coffee_bean_id": UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
                "image_exists": True,
                "coordinate": {"latitude": 1.0, "longitude": 1.0},
            },
        ),
        (
            {
                "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
                "rating": 4,
            },
            {
                "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
                "rating": 4,
                "brewing_method": None,
                "coffee_bean_id": None,
                "image_exists": False,
                "coordinate": None,
            },
        ),
    ],
)
def test_create_drink_schema_creation_success(
    input_object: Dict[str, Any], expected_dict: object
) -> None:
    """Test successful creation of a create drink schema."""
    drink = CreateDrink(**input_object)
    assert drink.model_dump(by_alias=True) == expected_dict


@pytest.mark.parametrize(
    "input_object,expected_exception",
    [
        (
            {
                "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
                "rating": 4,
                "brewing_method": "Espresso",
                "user_id": UUID("c9ba633e-c39c-11ed-afb4-acde48001122"),
                "coffee_bean_id": UUID("c9ba633e-c38c-11ed-afb4-acde48001122"),
                "image_exists": True,
                "coordinate": {"latitude": 1.0, "longitude": 1.0},
            },
            ValidationError,
        ),
        (
            {
                "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
            },
            ValueError,
        ),
    ],
)
def test_create_drink_schema_creation_failure(
    input_object: Dict[str, Any], expected_exception: Type[BaseException]
) -> None:
    """Test creation failure of a create drink schema."""
    with pytest.raises(expected_exception):
        Drink(**input_object)
