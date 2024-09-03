from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.drink import DrinkService
from tests.conftest import DummyDrinks


@pytest.mark.asyncio
async def test_drink_service_get_by_id(
    dummy_drinks: DummyDrinks,
) -> None:
    """Test the get_by_id drink service method

    Args:
        dummy_drinks (DummyDrinks): A fixture providing dummy drink objects.
    """
    drink_1 = dummy_drinks.drink_1

    drink_crud_mock = AsyncMock()
    drink_crud_mock.read.return_value = [drink_1]

    db_session_mock = AsyncMock()

    test_drink_service = DrinkService(drink_crud=drink_crud_mock)

    result = await test_drink_service.get_by_id(
        db_session=db_session_mock, drink_id=drink_1.id
    )
    drink_crud_mock.read.assert_awaited_once_with(
        db_session=db_session_mock, query={"_id": drink_1.id}
    )

    assert result == drink_1


@pytest.mark.asyncio
async def test_coffee_service_get_by_id_with_unknown_id(
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the list service method.

    Args:
        dummy_drinks (DummyDrinks): A fixture providing dummy drink objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """
    unknown_id = uuid7()

    drink_crud_mock = AsyncMock()
    drink_crud_mock.read.side_effect = ObjectNotFoundError("Test message")

    db_session_mock = AsyncMock()

    test_drink_service = DrinkService(drink_crud=drink_crud_mock)

    with pytest.raises(HTTPException) as http_error:
        await test_drink_service.get_by_id(
            db_session=db_session_mock, drink_id=unknown_id
        )

    assert str(http_error.value.detail) == "No drink found for given id"
