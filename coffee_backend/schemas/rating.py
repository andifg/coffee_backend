from typing import List

from pydantic import BaseModel, Field


class Rating(BaseModel):
    """Describes one rating"""

    id: str = Field(..., description="The id of the rating", example="1")
    rating: int = Field(..., description="Ratings for coffee")
