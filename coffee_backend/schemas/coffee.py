from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Extra, Field


class Coffee(BaseModel):
    """Describes a Coffee type"""

    id: UUID = Field(
        ...,
        alias="_id",
        description="The id of the coffee",
        example=UUID("123e4567-e89b-12d3-a456-426655440000"),
    )
    name: str = Field(..., description="Name of coffee")
    roasting_company: str = Field(
        ..., description="Name of the roasting company"
    )
    owner_id: UUID = Field(
        ...,
        description="The id of the owner of the coffee",
        example=UUID("123e4567-e89b-12d3-a456-426655440000"),
    )
    owner_name: str = Field(..., description="Name of the owner of the coffee")

    rating_count: Optional[int] = Field(
        default=None,
        description="The number of ratings for the coffee",
        example=3,
    )
    rating_average: Optional[float] = Field(
        default=None,
        description="The average rating for the coffee",
        example=4.5,
    )


class UpdateCoffee(BaseModel):
    """Describes the update schema for a Coffee"""

    name: str = Field(..., description="Name of coffee")

    roasting_company: str = Field(
        ..., description="Name of the roasting company"
    )

    owner_id: UUID = Field(
        ...,
        description="The id of the owner of the coffee",
        example=UUID("123e4567-e89b-12d3-a456-426655440000"),
    )

    owner_name: str = Field(..., description="Name of the owner of the coffee")

    class Config:
        """Pydantic config"""

        extra = Extra.forbid


class CreateCoffee(BaseModel):
    """Describes the create schema for a Coffee.

    As we get the owner id and name from the JWT token,
    we only need the name of the coffee and the uuid.
    """

    id: UUID = Field(
        ...,
        alias="_id",
        description="The id of the coffee",
        example=UUID("123e4567-e89b-12d3-a456-426655440000"),
    )
    name: str = Field(..., description="Name of coffee")

    roasting_company: str = Field(
        ..., description="Name of the roasting company"
    )

    class Config:
        """Pydantic config"""

        extra = Extra.forbid
