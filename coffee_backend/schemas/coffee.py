from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

from coffee_backend.schemas.rating import Rating


class Coffee(BaseModel):
    """Describes one email message"""

    id: UUID = Field(
        ...,
        alias="_id",
        description="The id of the coffee",
        example=UUID("123e4567-e89b-12d3-a456-426655440000"),
    )
    name: str = Field(..., description="Name of coffee")
    ratings: List[Rating] = Field(
        [], description="Ratings asociated with coffee"
    )
