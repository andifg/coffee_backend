from unittest.mock import MagicMock, call
from uuid import UUID

import pytest

from coffee_backend.services.coffee_image import ImageService
from tests.conftest import DummyImages


@pytest.mark.asyncio
async def test_coffee_image_service_delete_coffee_image(
    dummy_coffee_images: DummyImages,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the CoffeeImagesService delete_coffee_image method for deleting all
    coffee images for a coffee inside of small and original versions.

    """
    coffee_image_crud = MagicMock()
    coffee_image_crud.delete.return_value = None

    coffe_uuid = UUID("123e4567-e19b-12d3-a456-426655440000")

    test_coffee_service = ImageService(coffee_images_crud=coffee_image_crud)

    test_coffee_service.delete_coffee_image(coffe_uuid)

    assert coffee_image_crud.delete.call_count == 2

    coffee_image_crud.delete.assert_has_calls(
        [
            call("123e4567-e19b-12d3-a456-426655440000", "small"),
            call("123e4567-e19b-12d3-a456-426655440000", "original"),
        ]
    )

    assert (
        "Deleted all versions for coffee image for coffee with id "
        "123e4567-e19b-12d3-a456-426655440000" in caplog.text
    )
