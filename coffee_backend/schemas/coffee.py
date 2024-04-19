from uuid import UUID

from pydantic import BaseModel, Extra, Field


class Coffee(BaseModel):
    """Describes a Coffee"""

    id: UUID = Field(
        ...,
        alias="_id",
        description="The id of the coffee",
        example=UUID("123e4567-e89b-12d3-a456-426655440000"),
    )
    name: str = Field(..., description="Name of coffee")
    owner_id: UUID = Field(
        ...,
        description="The id of the owner of the coffee",
        example=UUID("123e4567-e89b-12d3-a456-426655440000"),
    )
    owner_name: str = Field(..., description="Name of the owner of the coffee")


class UpdateCoffee(BaseModel):
    """Describes the update schema for a Coffee"""

    name: str = Field(..., description="Name of coffee")

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

    class Config:
        """Pydantic config"""

        extra = Extra.forbid
