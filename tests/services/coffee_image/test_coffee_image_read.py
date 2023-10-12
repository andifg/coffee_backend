from unittest.mock import MagicMock
from uuid import UUID

import pytest
from fastapi import HTTPException

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.coffee_image import ImageService
from tests.conftest import DummyImages


@pytest.mark.asyncio
async def test_coffee_image_service_get_coffee_image(
    dummy_coffee_images: DummyImages,
) -> None:
    """Test the CoffeeImagesService get_coffee_image method for retrieving a
        coffee image.

    Args:
        dummy_coffee_images (DummyImages): An instance providing dummy coffee
            image data.

    """
    coffee_image_crud = MagicMock()
    coffee_image_crud.read.return_value = (
        dummy_coffee_images.image_1_bytes,
        "jpg",
    )

    coffe_uuid = UUID("123e4567-e19b-12d3-a456-426655440000")

    test_coffee_service = ImageService(coffee_images_crud=coffee_image_crud)

    result = test_coffee_service.get_coffee_image(coffe_uuid)

    assert coffee_image_crud.read.call_count == 1

    coffee_image_crud.read.assert_called_once_with(
        "123e4567-e19b-12d3-a456-426655440000"
    )

    assert result == (dummy_coffee_images.image_1_bytes, "jpg")


@pytest.mark.asyncio
async def test_coffee_image_service_get_coffee_image_object_not_found(
    dummy_coffee_images: DummyImages,
) -> None:
    """Test the CoffeeImagesService get_coffee_image method when the object is
        not found.

    Args:
        dummy_coffee_images (DummyImages): An instance providing dummy coffee
        image data.

    Raises:
        pytest.raises(HTTPException): An HTTPException should be raised when
        the requested coffee image is not found in the S3 bucket.

    """

    coffee_image_crud = MagicMock()
    coffee_image_crud.read.side_effect = ObjectNotFoundError(
        message="Object not found"
    )

    coffe_uuid = UUID("123e4567-e19b-12d3-a456-426655440000")

    test_coffee_service = ImageService(coffee_images_crud=coffee_image_crud)

    with pytest.raises(HTTPException):
        test_coffee_service.get_coffee_image(coffe_uuid)
