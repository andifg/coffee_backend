from unittest.mock import MagicMock
from uuid import UUID

import pytest
from fastapi import HTTPException

from coffee_backend.services.coffee_image import CoffeeImagesService
from tests.conftest import DummyImages


@pytest.mark.asyncio
async def test_coffee_image_service_add_coffee_image(
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

    coffee_image_crud = MagicMock()
    coffee_image_crud.create.return_value = None

    coffe_uuid = UUID("123e4567-e19b-12d3-a456-426655440000")

    test_coffee_service = CoffeeImagesService(
        coffee_images_crud=coffee_image_crud
    )

    test_coffee_service.add_coffee_image(image_1, coffe_uuid)

    assert coffee_image_crud.create.call_count == 1

    coffee_image_crud.create.assert_called_once_with(
        "123e4567-e19b-12d3-a456-426655440000", image_1.file, "jpg"
    )

    assert (
        "Added coffee image for coffee with id "
        "123e4567-e19b-12d3-a456-426655440000" in caplog.text
    )


@pytest.mark.asyncio
async def test_coffee_image_service_add_coffee_without_filename(
    dummy_coffee_images: DummyImages,
) -> None:
    """Test the CoffeeImagesService add_coffee_image method when no filename
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

    coffee_image_crud = MagicMock()
    coffee_image_crud.create.return_value = None

    coffe_uuid = UUID("123e4567-e19b-12d3-a456-426655440000")

    test_coffee_service = CoffeeImagesService(
        coffee_images_crud=coffee_image_crud
    )

    with pytest.raises(HTTPException):
        test_coffee_service.add_coffee_image(image_1, coffe_uuid)
