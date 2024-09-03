from unittest.mock import AsyncMock

import pytest

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.drink import DrinkService
from tests.conftest import DummyDrinks


@pytest.mark.asyncio
async def test_drink_service_read(
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the list service method.

    Args:
        dummy_drinks (DummyDrinks): A fixture providing dummy drink objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """
    drink_1 = dummy_drinks.drink_1
    drink_2 = dummy_drinks.drink_2

    coffee_crud_mock = AsyncMock()
    coffee_crud_mock.read.return_value = [drink_1, drink_2]

    db_session_mock = AsyncMock()

    test_drink_service = DrinkService(drink_crud=coffee_crud_mock)

    result = await test_drink_service.list(
        db_session=db_session_mock,
    )
    coffee_crud_mock.read.assert_awaited_once_with(
        db_session=db_session_mock, query={}, limit=5, skip=0
    )

    assert result == [drink_1, drink_2]


@pytest.mark.asyncio
async def test_drink_service_read_with_empty_db_coffee_collection(
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the list service method to return an emtpy error if no drinks
        are found.

    Args:
        dummy_drinks (DummyDrinks): A fixture providing dummy coffee objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """

    drink_crud_mock = AsyncMock()
    drink_crud_mock.read.side_effect = ObjectNotFoundError("Test message")

    db_session_mock = AsyncMock()

    test_drink_service = DrinkService(drink_crud=drink_crud_mock)

    result = await test_drink_service.list(
        db_session=db_session_mock,
    )

    assert result == []
