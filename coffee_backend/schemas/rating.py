from enum import Enum
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


class Rating(BaseModel):
    """Describes one rating"""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    id: UUID = Field(
        ...,
        alias="_id",
        description="The id of the rating",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440000")],
    )
    brewing_method: BrewingMethod = Field(..., description="Brewing method")
    rating: float = Field(..., description="Ratings for coffee")
    coffee_id: UUID = Field(
        ...,
        description="The id of the coffee",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440001")],
    )
    user_id: UUID = Field(
        ...,
        description="The id of the user created the rating",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440000")],
    )
    user_name: str = Field(
        ...,
        description="Name of the user created the rating",
        examples=["Andi", "John"],
    )
    image_exists: bool = Field(
        default=False,
        description="Whether rating was submitted with or without a picture",
    )


class CreateRating(BaseModel):
    """Describes the request body for creating a rating

    We get the user id and name from the JWT token.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    id: UUID = Field(
        ...,
        alias="_id",
        description="The id of the rating",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440000")],
    )
    brewing_method: BrewingMethod = Field(..., description="Brewing method")
    rating: float = Field(..., description="Ratings for coffee")
    coffee_id: UUID = Field(
        ...,
        description="The id of the coffee",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440001")],
    )
    image_exists: bool = Field(
        default=False,
        description="Whether rating was submitted with or without a picture",
    )
