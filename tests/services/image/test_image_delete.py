from unittest.mock import MagicMock, call
from uuid import UUID

import pytest

from coffee_backend.schemas import ImageType
from coffee_backend.services.image_service import ImageService
from tests.conftest import DummyImages


@pytest.mark.asyncio
async def test_image_service_delete_coffee_image(
    dummy_coffee_images: DummyImages,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the ImagesService delete_image method for deleting all
    images for a coffee_drink inside of small and original versions.

    """
    object_image_crud = MagicMock()
    object_image_crud.delete.return_value = None

    coffe_uuid = UUID("123e4567-e19b-12d3-a456-426655440000")

    test_coffee_service = ImageService(object_crud=object_image_crud)

    test_coffee_service.delete_image(
        object_id=coffe_uuid, image_type=ImageType.COFFEE_DRINK
    )

    assert object_image_crud.delete.call_count == 2

    object_image_crud.delete.assert_has_calls(
        [
            call(
                filepath="coffee_drink/small",
                filename="123e4567-e19b-12d3-a456-426655440000",
            ),
            call(
                filepath="coffee_drink/original",
                filename="123e4567-e19b-12d3-a456-426655440000",
            ),
        ]
    )

    assert (
        "Deleted all versions for coffee_drink image with id "
        "123e4567-e19b-12d3-a456-426655440000" in caplog.text
    )
