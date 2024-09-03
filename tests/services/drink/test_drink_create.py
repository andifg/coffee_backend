from unittest.mock import AsyncMock

import pytest

from coffee_backend.services.drink import DrinkService
from tests.conftest import DummyDrinks


@pytest.mark.asyncio
async def test_drink_service_create(
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the create service method with a new drink.

    This test verifies the behavior of the add_coffee method in the
    CoffeeService class when adding a new coffee object that does not already
    exist in the database.

    Args:
        dummy_drinks (DummyDrinks): A fixture providing dummy drink objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """
    drink_1 = dummy_drinks.drink_1

    drink_crud_mock = AsyncMock()
    drink_crud_mock.create.return_value = drink_1

    db_session_mock = AsyncMock()

    test_coffee_service = DrinkService(drink_crud=drink_crud_mock)

    result = await test_coffee_service.add_drink(
        drink=drink_1, db_session=db_session_mock
    )
    drink_crud_mock.create.assert_awaited_once_with(
        db_session=db_session_mock, drink=drink_1
    )

    assert result == drink_1
