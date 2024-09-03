from unittest.mock import AsyncMock

import pytest
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.drink import DrinkService
from tests.conftest import DummyDrinks


@pytest.mark.asyncio
async def test_drink_service_delete_by_coffee_bean_id(
    dummy_drinks: DummyDrinks,
) -> None:
    """
    Test deleting all drinks for a coffee.

    Args:
        dummy_drinks (DummyDrinks): A fixture providing dummy drink objects.
    """

    drink_1 = dummy_drinks.drink_1

    drink_crud_mock = AsyncMock()

    db_session_mock = AsyncMock()

    test_drink_service = DrinkService(drink_crud=drink_crud_mock)

    await test_drink_service.delete_by_coffee_bean_id(
        db_session=db_session_mock, coffee_bean_id=drink_1.coffee_bean_id
    )
    drink_crud_mock.delete_many.assert_awaited_once_with(
        db_session=db_session_mock,
        query={"coffee_bean_id": drink_1.coffee_bean_id},
    )


@pytest.mark.asyncio
async def test_drink_service_delete_by_coffee_id_with_unknown_id(
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Ensuring none is returned when no drinks are found for a coffee.

    Args:
        dummy_drinks (DummyDrinks): A fixture providing dummy drink objects.
        caplog (pytest.LogCaptureFixture): The log capture fixture.
    """

    unknown_id = uuid7()

    drink_crud_mock = AsyncMock()
    drink_crud_mock.delete_many.side_effect = ObjectNotFoundError(
        "Test message"
    )

    db_session_mock = AsyncMock()

    test_drink_service = DrinkService(drink_crud=drink_crud_mock)

    await test_drink_service.delete_by_coffee_bean_id(
        db_session=db_session_mock, coffee_bean_id=unknown_id
    )

    drink_crud_mock.delete_many.assert_awaited_once_with(
        db_session=db_session_mock, query={"coffee_bean_id": unknown_id}
    )
