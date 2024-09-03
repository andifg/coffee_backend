from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from uuid_extensions.uuid7 import uuid7

from coffee_backend.api.authorization import authorize_coffee_edit_delete
from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas import ImageType
from tests.conftest import DummyCoffees, TestApp


@patch("coffee_backend.api.v1.coffees.authorize_coffee_edit_delete")
@patch("coffee_backend.services.image_service.ImageService.delete_image")
@patch("coffee_backend.services.rating.DrinkService.delete_by_coffee_id")
@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@patch("coffee_backend.services.coffee.CoffeeService.delete_coffee")
@pytest.mark.asyncio
async def test_api_delete_coffee_by_id(
    coffee_service_mock: AsyncMock,
    coffee_service_get_by_id_mock: AsyncMock,
    drink_service_mock: AsyncMock,
    image_service_mock: AsyncMock,
    authorize_coffee_edit_delete_mock: MagicMock,
    test_app: TestApp,
    dummy_coffees: DummyCoffees,
    mock_security_dependency: Generator,
) -> None:
    """
    Test deleting a coffee by ID.

    Args:
        coffee_service_mock (AsyncMock): The mocked CoffeeService delete coffee method.
        coffee_service_get_by_id_mock (AsyncMock): The mocked CoffeeService
            get_by_id method.
        drink_service_mock (AsyncMock): The mocked DrinkService.
        image_service_mock (AsyncMock): The mocked ImageService.
        authorize_coffee_edit_delete_mock (MagicMock): The mocked authorization check.
        test_app (TestApp): The test application.
        dummy_coffees (DummyCoffees): The dummy coffees fixture.
        mock_security_dependency: Fixture to mock the authentication
            and authorization check within api to always return True
    """

    get_db_mock = AsyncMock()

    coffee_service_get_by_id_mock.return_value = dummy_coffees.coffee_1

    authorize_coffee_edit_delete_mock.return_value = None

    app.dependency_overrides[get_db] = lambda: get_db_mock

    response = await test_app.client.delete(
        f"/api/v1/coffees/{dummy_coffees.coffee_1.id}",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.text == ""

    coffee_service_get_by_id_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=dummy_coffees.coffee_1.id
    )

    drink_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=dummy_coffees.coffee_1.id
    )

    image_service_mock.assert_called_once_with(
        object_id=dummy_coffees.coffee_1.id, image_type=ImageType.COFFEE_BEAN
    )

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=dummy_coffees.coffee_1.id
    )

    app.dependency_overrides = {}


@patch("coffee_backend.api.v1.coffees.authorize_coffee_edit_delete")
@patch("coffee_backend.services.image_service.ImageService.delete_image")
@patch("coffee_backend.services.rating.DrinkService.delete_by_coffee_id")
@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@patch("coffee_backend.services.coffee.CoffeeService.delete_coffee")
@pytest.mark.asyncio
async def test_api_delete_coffee_by_id_with_unkown_id(
    coffee_service_mock: AsyncMock,
    coffee_service_get_by_id_mock: AsyncMock,
    drink_service_mock: AsyncMock,
    image_service_mock: AsyncMock,
    authorize_coffee_edit_delete_mock: MagicMock,
    test_app: TestApp,
    mock_security_dependency: Generator,
) -> None:
    """
    Ensuring error is returned when id is not known.

    Args:
        coffee_service_mock (AsyncMock): The mocked CoffeeService delete coffee method.
        coffee_service_get_by_id_mock (AsyncMock): The mocked CoffeeService
            get_by_id method.
        drink_service_mock (AsyncMock): The mocked DrinkService.
        image_service_mock (AsyncMock): The mocked ImageService.
        authorize_coffee_edit_delete_mock (MagicMock): The mocked authorization check.
        test_app (TestApp): The test application.
        dummy_coffees (DummyCoffees): The dummy coffees fixture.
        mock_security_dependency: Fixture to mock the authentication
            and authorization check within api to always return True.
    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_get_by_id_mock.side_effect = HTTPException(
        status_code=404, detail="No coffee found for given id"
    )

    unkown_id = uuid7()

    response = await test_app.client.delete(
        f"/api/v1/coffees/{unkown_id}",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "No coffee found for given id"}

    coffee_service_get_by_id_mock.assert_awaited_once_with(
        db_session=get_db_mock, coffee_id=unkown_id
    )

    authorize_coffee_edit_delete_mock.assert_not_called()

    drink_service_mock.assert_not_awaited()

    image_service_mock.assert_not_called()

    coffee_service_mock.assert_not_awaited()

    app.dependency_overrides = {}
