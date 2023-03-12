from typing import List

from pydantic import BaseModel, Field

from coffee_backend.schemas.rating import Rating


class Coffee(BaseModel):
    """Describes one email message"""

    id: str = Field(..., description="The id of the coffee", example="1")
    name: str = Field(..., description="Name of coffee")
    ratings: List[Rating] = Field([], description="Ratings asociated with coffee")
