from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Coffee(BaseModel):
    """Describes a Coffee type"""

    id: UUID = Field(
        ...,
        alias="_id",
        description="The id of the coffee",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440000")],
    )
    name: str = Field(..., description="Name of coffee")
    roasting_company: str = Field(
        ..., description="Name of the roasting company"
    )
    owner_id: UUID = Field(
        ...,
        description="The id of the owner of the coffee",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440000")],
    )
    owner_name: str = Field(..., description="Name of the owner of the coffee")

    rating_count: Optional[int] = Field(
        default=None,
        description="The number of ratings for the coffee",
        examples=[3],
    )
    rating_average: Optional[float] = Field(
        default=None,
        description="The average rating for the coffee",
        examples=[4.5],
    )


class UpdateCoffee(BaseModel):
    """Describes the update schema for a Coffee"""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Name of coffee")

    roasting_company: str = Field(
        ..., description="Name of the roasting company"
    )

    owner_id: UUID = Field(
        ...,
        description="The id of the owner of the coffee",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440000")],
    )

    owner_name: str = Field(..., description="Name of the owner of the coffee")


class CreateCoffee(BaseModel):
    """Describes the create schema for a Coffee.

    As we get the owner id and name from the JWT token,
    we only need the name of the coffee and the uuid.
    """

    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(
        ...,
        alias="_id",
        description="The id of the coffee",
        examples=[UUID("123e4567-e89b-12d3-a456-426655440000")],
    )
    name: str = Field(..., description="Name of coffee")

    roasting_company: str = Field(
        ..., description="Name of the roasting company"
    )
