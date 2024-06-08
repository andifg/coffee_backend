from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class BrewingMethod(Enum):
    """Describes brewing methods"""

    ESPRESSO = "Espresso"
    CAPPUCCINO = "Cappuccino"
    LATTE = "Latte"
    AMERICANO = "Americano"


class Rating(BaseModel):
    """Describes one rating"""

    id: UUID = Field(
        ...,
        alias="_id",
        description="The id of the rating",
        example=UUID("123e4567-e89b-12d3-a456-426655440000"),
    )
    brewing_method: BrewingMethod = Field(..., description="Brewing method")
    rating: float = Field(..., description="Ratings for coffee")
    coffee_id: UUID = Field(
        ...,
        description="The id of the coffee",
        example=UUID("123e4567-e89b-12d3-a456-426655440001"),
    )
    user_id: UUID = Field(
        ...,
        description="The id of the user created the rating",
        example=UUID("123e4567-e89b-12d3-a456-426655440000"),
    )
    user_name: str = Field(
        ..., description="Name of the user created the rating"
    )
