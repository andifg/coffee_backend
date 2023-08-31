from typing import List
from uuid import UUID

from pydantic import BaseModel, Extra, Field

from coffee_backend.schemas.rating import Rating


class Coffee(BaseModel):
    """Describes a Coffee"""

    id: UUID = Field(
        ...,
        alias="_id",
        description="The id of the coffee",
        example=UUID("123e4567-e89b-12d3-a456-426655440000"),
    )
    name: str = Field(..., description="Name of coffee")


class UpdateCoffee(BaseModel):
    """Describes the update schema for a Coffee"""

    name: str = Field(..., description="Name of coffee")

    class Config:
        """Pydantic config"""

        extra = Extra.forbid
