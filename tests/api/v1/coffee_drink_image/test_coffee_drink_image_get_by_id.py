from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from uuid_extensions.uuid7 import uuid7

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyCoffees, DummyImages, TestApp


@patch("coffee_backend.services.image_service.ImageService.get_image")
@pytest.mark.asyncio
async def test_api_get_coffee_drink_image_by_id(
    image_service_mock: MagicMock,
    test_app: TestApp,
    dummy_coffee_images: DummyImages,
    mock_security_dependency: Generator,
) -> None:
    """Test the API endpoint to retrieve a coffee drink image by its ID.

    Args:
        image_service_mock (MagicMock): A mock object for the ImageService.
        test_app (TestApp): An instance of the TestApp for testing.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True
    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    image_service_mock.return_value = (
        dummy_coffee_images.image_1_bytes,
        "jpg",
    )

    coffee_drink_id = UUID("123e4567-e19b-12d3-a456-426655440000")

    response = await test_app.client.get(
        f"/api/v1/coffee-drink/{coffee_drink_id}/image",
        headers={"Content-Type": "multipart/form-data"},
    )

    assert response.status_code == 200
    assert response.content == dummy_coffee_images.image_1_bytes

    assert response.headers["Content-Type"] == "image/jpg"

    assert (
        response.headers["Content-Disposition"]
        == f"attachment; filename={coffee_drink_id}.jpg"
    )

    image_service_mock.assert_called_once()

    app.dependency_overrides = {}


@patch("coffee_backend.services.image_service.ImageService.get_image")
@pytest.mark.asyncio
async def test_api_get_coffee_drink_image_by_id_nonexisting(
    image_service_mock: MagicMock,
    test_app: TestApp,
    dummy_coffee_images: DummyImages,
    mock_security_dependency: Generator,
) -> None:
    """Test API endpoint to retrieve a non-existing coffee drink image by ID.

    Args:
        image_service_mock (MagicMock): A mock object for the ImageService.
        test_app (TestApp): An instance of the TestApp for testing.
        dummy_coffee_images (DummyImages): A fixture providing dummy coffee images.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True
    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    image_service_mock.side_effect = HTTPException(
        status_code=404, detail="Coffee image not found"
    )

    coffee_drink_id = UUID("123e4567-e19b-12d3-a456-426655440000")

    response = await test_app.client.get(
        f"/api/v1/coffee-drink/{coffee_drink_id}/image",
        headers={"Content-Type": "multipart/form-data"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Coffee image not found"}

    image_service_mock.assert_called_once()

    app.dependency_overrides = {}
