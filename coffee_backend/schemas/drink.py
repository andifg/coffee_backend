from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BrewingMethod(Enum):
    """Describes brewing methods"""

    ESPRESSO = "Espresso"
    CAPPUCCINO = "Cappuccino"
    LATTE = "Latte"
    AMERICANO = "Americano"
    FILTER = "Filter"
    BIALETTI = "Bialetti"


class Drink(BaseModel):
    """Describes one rating"""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    id: UUID = Field(
        ...,
        alias="_id",
        description="The id of the drink",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440000")],
    )
    brewing_method: Optional[BrewingMethod] = Field(
        description="If drink is a coffee, this field"
        + " describes the brewing method",
        default=None,
    )
    rating: float = Field(..., description="Rating of the drink")
    coffee_bean_id: Optional[UUID] = Field(
        description="If the drink is made from a specific coffee bean "
        + "this is the id of the coffee bean",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440001")],
        default=None,
    )
    user_id: UUID = Field(
        ...,
        description="The id of the user created the drink",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440000")],
    )
    user_name: str = Field(
        ...,
        description="Name of the user created the drink",
        examples=["Andi", "John"],
    )
    image_exists: Optional[bool] = Field(
        default=False,
        description="Whether drink was submitted with or without a picture",
    )
    coffee_bean_name: Optional[str] = Field(
        default=None,
        description="Name of the coffee bean",
    )
    coffee_bean_roasting_company: Optional[str] = Field(
        default=None,
        description="Name of the roasting company",
    )


class CreateDrink(BaseModel):
    """Describes the request body for creating a drink

    We get the user id and name from the JWT token.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    id: UUID = Field(
        ...,
        alias="_id",
        description="The id of the drink",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440000")],
    )
    brewing_method: Optional[BrewingMethod] = Field(
        description="Brewing method", default=None
    )
    rating: float = Field(..., description="Rating of the drink")
    coffee_bean_id: Optional[UUID] = Field(
        description="If the drink is made from a specific coffee bean, this is"
        + " the id of the coffee bean",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440001")],
        default=None,
    )
    image_exists: Optional[bool] = Field(
        default=False,
        description="Whether drink was submitted with or without a picture",
    )
