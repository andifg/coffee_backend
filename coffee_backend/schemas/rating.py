from uuid import UUID

from pydantic import BaseModel, Field


class Rating(BaseModel):
    """Describes one rating"""

    id: UUID = Field(
        ...,
        alias="_id",
        description="The id of the rating",
        example=UUID("123e4567-e89b-12d3-a456-426655440000"),
    )
    rating: int = Field(..., description="Ratings for coffee")
