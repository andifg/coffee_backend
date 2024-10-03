from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from uuid_extensions.uuid7 import uuid7

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyCoffees, DummyDrinks, TestApp


@patch("coffee_backend.services.drink.DrinkService.delete_drink")
@pytest.mark.asyncio
async def test_api_delete_drink_by_id(
    drink_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_drinks: DummyDrinks,
    mock_security_dependency: Generator,
) -> None:
    """
    Test deleting a drink by ID.

    Args:
        drink_service_mock (AsyncMock): The mocked DrinkService.
        test_app (TestApp): The test application.
        dummy_drink (DummyDrinks): The dummy drinks fixture.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True
    """
    drink_1 = dummy_drinks.drink_1

    get_db_mock = AsyncMock()

    drink_service_mock.return_value = "Return without error"

    app.dependency_overrides[get_db] = lambda: get_db_mock

    response = await test_app.client.delete(
        f"/api/v1/drinks/{drink_1.id}",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.text == ""

    drink_service_mock.assert_awaited_once_with(
        db_session=get_db_mock, drink_id=drink_1.id
    )

    app.dependency_overrides = {}
