from uuid import UUID

from pydantic import BaseModel, Field


class RatingSummary(BaseModel):
    """Describes one rating summary."""

    coffee_id: UUID = Field(
        ...,
        description="The id of the coffee",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440000")],
    )
    rating_count: int = Field(
        ..., description="Number of ratings for coffee", examples=[5]
    )
    rating_average: float = Field(
        ...,
        description="The current average rating for the coffee",
        examples=[4.5],
    )
