from unittest.mock import MagicMock
from uuid import UUID

import pytest
from fastapi import HTTPException

from coffee_backend.schemas import CoffeeDrinkImage
from coffee_backend.services.image_service import ImageService
from tests.conftest import DummyImages


@pytest.mark.asyncio
async def test_image_service_add_coffee_image(
    dummy_coffee_images: DummyImages,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the CoffeeImagesService add_coffee_image method for adding a coffee
        image.


    Args:
        dummy_coffee_images (DummyImages): An instance providing dummy coffee
            image data.
        caplog (pytest.LogCaptureFixture): A fixture for capturing log output.
    """
    image_1 = dummy_coffee_images.image_1

    object_image_crud = MagicMock()
    object_image_crud.create.return_value = None

    coffe_uuid = UUID("123e4567-e19b-12d3-a456-426655440000")

    test_coffee_service = ImageService(object_crud=object_image_crud)

    test_coffee_service.add_image(
        CoffeeDrinkImage(
            key=coffe_uuid,
            file=image_1,
        )
    )

    assert object_image_crud.create.call_count == 1

    object_image_crud.create.assert_called_once_with(
        filepath="coffee_drink/original",
        filename="123e4567-e19b-12d3-a456-426655440000",
        file=image_1.file,
        file_type="jpeg",
    )

    assert (
        "Added object coffee_drink with key "
        "123e4567-e19b-12d3-a456-426655440000" in caplog.text
    )


@pytest.mark.asyncio
async def test_image_service_add_coffee_without_filename(
    dummy_coffee_images: DummyImages,
) -> None:
    """Test the ImagesService add_object method when no filename
        is provided.

    Args:
        dummy_coffee_images (DummyImages): An instance providing dummy coffee
        image data.

    Raises:
        pytest.raises(HTTPException): An HTTPException should be raised when
        attempting to add a coffee image without a filename.
    """
    image_1 = dummy_coffee_images.image_1

    image_1.filename = None

    object_image_crud = MagicMock()
    object_image_crud.create.return_value = None

    coffe_uuid = UUID("123e4567-e19b-12d3-a456-426655440000")

    test_coffee_service = ImageService(object_crud=object_image_crud)

    with pytest.raises(HTTPException):
        test_coffee_service.add_image(
            CoffeeDrinkImage(
                key=coffe_uuid,
                file=image_1,
            )
        )
