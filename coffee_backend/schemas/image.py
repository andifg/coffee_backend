from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID

from fastapi import UploadFile


class ImageType(Enum):
    """Describe the type of image."""

    COFFEE_DRINK = "coffee_drink"
    COFFEE_BEAN = "coffee_bean"


@dataclass
class S3Object(ABC):
    """Describes the object to be stored in S3."""

    key: UUID
    file: UploadFile
    type: ImageType = field(init=False)
    context_path: str = field(init=False)


@dataclass
class CoffeeDrinkImage(S3Object):
    """Describes a coffee drink image to be stored in S3."""

    key: UUID
    file: UploadFile

    def __post_init__(self) -> None:
        self.context_path = "coffee_drink"
        self.type = ImageType.COFFEE_DRINK


@dataclass
class CoffeeBeanImage(S3Object):
    """Describes a coffee bean image to be stored in S3."""

    key: UUID
    file: UploadFile

    def __post_init__(self) -> None:
        self.context_path = "coffee_bean"
        self.type = ImageType.COFFEE_BEAN
