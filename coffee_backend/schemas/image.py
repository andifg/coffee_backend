from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal
from uuid import UUID

from fastapi import UploadFile


class ImageType(Enum):
    COFFEE_DRINK = "coffee_drink"
    COFFEE_BEAN = "coffee_bean"


@dataclass
class S3Object(ABC):
    key: UUID
    file: UploadFile
    type: ImageType = field(init=False)
    contextPath: str = field(init=False)


@dataclass
class CoffeeDrinkImage(S3Object):
    key: UUID
    file: UploadFile

    def __post_init__(self) -> None:
        self.contextPath = "coffee_drink"
        self.type = "coffee_drink"
