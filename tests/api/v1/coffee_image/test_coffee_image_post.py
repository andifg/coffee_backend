import io
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from starlette.datastructures import Headers, UploadFile

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyCoffees, DummyImages, TestApp


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@patch("coffee_backend.services.coffee_image.ImageService.add_coffee_image")
@pytest.mark.asyncio
async def test_api_create_coffee(
    coffee_image_service_mock: MagicMock,
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_coffee_images: DummyImages,
) -> None:
    """Test the API endpoint for creating a coffee image.

    Args:
        coffee_image_service_mock (MagicMock): A mock of the CoffeeImagesService.
        coffee_service_mock (AsyncMock): A mock of the CoffeeService.
        test_app (TestApp): A FastAPI test client.
        dummy_coffee_images (DummyImages): An instance providing dummy coffee
            image data.
    """

    get_db_mock = MagicMock()

    coffee_service_mock.return_value = "Return without error"

    coffee_image_service_mock.return_value = "Return without error"

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_id = UUID("123e4567-e19b-12d3-a456-426655440000")

    response = await test_app.client.post(
        f"/api/v1/coffees/{coffee_id}/image",
        files={
            "file": (
                "testfile.jpeg",
                dummy_coffee_images.image_1_bytes,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 201

    coffee_image_service_mock.assert_called_once()

    app.dependency_overrides = {}


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@pytest.mark.asyncio
async def test_api_create_coffee_for_nonexisting_coffee(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_coffee_images: DummyImages,
) -> None:
    """Test the API endpoint for creating a coffee image for a
        non-existing coffee.

    Args:
        coffee_service_mock (AsyncMock): A mock of the CoffeeService.
        test_app (TestApp): A FastAPI test client.
        dummy_coffee_images (DummyImages): An instance providing dummy coffee image data.
    """

    get_db_mock = MagicMock()

    coffee_service_mock.side_effect = HTTPException(
        status_code=404, detail="Coffee not found"
    )

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_id = UUID("123e4567-e19b-12d3-a456-426655440000")

    response = await test_app.client.post(
        f"/api/v1/coffees/{coffee_id}/image",
        files={
            "file": (
                "testfile.jpeg",
                dummy_coffee_images.image_1_bytes,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 404

    assert response.json() == {"detail": "Coffee not found"}

    app.dependency_overrides = {}
