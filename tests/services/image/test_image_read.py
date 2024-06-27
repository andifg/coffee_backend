from unittest.mock import MagicMock, call
from uuid import UUID

import pytest
from fastapi import HTTPException

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.schemas import ImageType
from coffee_backend.services.image_service import ImageService
from tests.conftest import DummyImages


@pytest.mark.asyncio
async def test_image_service_get_image_small_existing(
    dummy_coffee_images: DummyImages,
) -> None:
    """Test coffee image service with existing small image.

    Test the ImagesService get_image method for retrieving a
        coffee_drink image from the S3 bucket when the small image exists.

    Args:
        dummy_coffee_images (DummyImages): An instance providing dummy
            image data.

    """
    object_image_crud = MagicMock()
    object_image_crud.read.return_value = (
        dummy_coffee_images.image_1_bytes,
        "jpg",
    )

    coffe_uuid = UUID("123e4567-e19b-12d3-a456-426655440000")

    test_image_service = ImageService(object_crud=object_image_crud)

    result = test_image_service.get_image(
        object_id=coffe_uuid, image_type=ImageType.COFFEE_DRINK
    )

    assert object_image_crud.read.call_count == 1

    object_image_crud.read.assert_called_once_with(
        filepath="coffee_drink/small",
        filename="123e4567-e19b-12d3-a456-426655440000",
    )

    assert result == (dummy_coffee_images.image_1_bytes, "jpg")


@pytest.mark.asyncio
async def test_image_service_get_image_small_not_existing(
    dummy_coffee_images: DummyImages,
) -> None:
    """Test image service with small image not existing.

    Test the ImagesService get_image method for retrieving a coffee_bean image
    from the S3 bucket when the small image not exists, but the original.

    Args:
        dummy_coffee_images (DummyImages): An instance providing dummy
            image data.

    """
    object_image_crud = MagicMock()

    object_image_crud.read.side_effect = [
        ObjectNotFoundError(message="Object not found"),
        (dummy_coffee_images.image_1_bytes, "jpg"),
    ]

    coffe_uuid = UUID("123e4567-e19b-12d3-a456-426655440000")

    test_coffee_service = ImageService(object_crud=object_image_crud)

    result = test_coffee_service.get_image(
        object_id=coffe_uuid, image_type=ImageType.COFFEE_BEAN
    )

    object_image_crud.read.assert_has_calls(
        [
            call(
                filepath="coffee_bean/small",
                filename="123e4567-e19b-12d3-a456-426655440000",
            ),
            call(
                filepath="coffee_bean/original",
                filename="123e4567-e19b-12d3-a456-426655440000",
            ),
        ]
    )

    assert object_image_crud.read.call_count == 2

    assert result == (dummy_coffee_images.image_1_bytes, "jpg")


@pytest.mark.asyncio
async def test_image_service_get_image_object_not_found(
    dummy_coffee_images: DummyImages,
) -> None:
    """Test the ImagesService get_image method when the object is not found.

    Args:
        dummy_coffee_images (DummyImages): An instance providing dummy
        image data.

    Raises:
        pytest.raises(HTTPException): An HTTPException should be raised when
        the requested coffee image is not found in the S3 bucket.

    """

    object_image_crud = MagicMock()
    object_image_crud.read.side_effect = ObjectNotFoundError(
        message="Object not found"
    )

    coffe_uuid = UUID("123e4567-e19b-12d3-a456-426655440000")

    test_coffee_service = ImageService(object_crud=object_image_crud)

    with pytest.raises(HTTPException):
        test_coffee_service.get_image(
            object_id=coffe_uuid, image_type=ImageType.COFFEE_DRINK
        )

    assert object_image_crud.read.call_count == 2
