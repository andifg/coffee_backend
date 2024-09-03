import io
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from fastapi.exceptions import HTTPException
from starlette.datastructures import Headers as Headers

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyImages, TestApp


@patch("coffee_backend.services.rating.DrinkService.get_by_id")
@patch("coffee_backend.services.image_service.ImageService.add_image")
@pytest.mark.asyncio
async def test_api_create_coffee_drink_image(
    image_service_mock: MagicMock,
    drink_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_coffee_images: DummyImages,
    mock_security_dependency: Generator,
) -> None:
    """Test the API endpoint for creating a coffee drink image.

    Args:
        image_service_mock (MagicMock): A mock of the ImagesService.
        drink_service_mock (AsyncMock): A mock of the DrinkService.
        test_app (TestApp): A FastAPI test client.
        dummy_coffee_images (DummyImages): An instance providing dummy
            image data.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True
    """

    get_db_mock = MagicMock()

    drink_service_mock.return_value = "Return without error"

    image_service_mock.return_value = "Return without error"

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_drink_id = UUID("123e4567-e19b-12d3-a456-426655440000")

    response = await test_app.client.post(
        f"/api/v1/coffee-drink/{coffee_drink_id}/image",
        files={
            "file": (
                "testfile.jpeg",
                dummy_coffee_images.image_1_bytes,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 201

    image_service_mock.assert_called_once()

    app.dependency_overrides = {}


@patch("coffee_backend.services.rating.DrinkService.get_by_id")
@pytest.mark.asyncio
async def test_api_create_image_for_nonexisting_coffee_drink(
    drink_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_coffee_images: DummyImages,
    mock_security_dependency: Generator,
) -> None:
    """Test the API endpoint for creating a coffee image for a
        non-existing coffee.

    Args:
        drink_service_mock (AsyncMock): A mock of the DrinkService.
        test_app (TestApp): A FastAPI test client.
        dummy_coffee_images (DummyImages): An instance providing dummy
            image data.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True
    """

    get_db_mock = MagicMock()

    drink_service_mock.side_effect = HTTPException(
        status_code=404, detail="Rating not found"
    )

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_drink_id = UUID("123e4567-e19b-12d3-a456-426655440000")

    response = await test_app.client.post(
        f"/api/v1/coffee-drink/{coffee_drink_id}/image",
        files={
            "file": (
                "testfile.jpeg",
                dummy_coffee_images.image_1_bytes,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 404

    assert response.json() == {"detail": "Rating not found"}

    app.dependency_overrides = {}
