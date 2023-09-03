from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.coffee import CoffeeService
from tests.conftest import DummyCoffees


@pytest.mark.asyncio
async def test_coffee_service_delete_by_id(
    dummy_coffees: DummyCoffees,
) -> None:
    """
    Test deleting a coffee by ID.

    Args:
        dummy_coffees (DummyCoffees): The dummy coffees fixture.
    """

    coffee_1 = dummy_coffees.coffee_1

    coffee_crud_mock = AsyncMock()

    db_session_mock = AsyncMock()

    test_coffee_service = CoffeeService(coffee_crud=coffee_crud_mock)

    await test_coffee_service.delete_coffee(
        db_session=db_session_mock, coffee_id=coffee_1.id
    )
    coffee_crud_mock.delete.assert_awaited_once_with(
        db_session=db_session_mock, coffee_id=coffee_1.id
    )


@pytest.mark.asyncio
async def test_coffee_service_delete_by_id_with_unknown_id(
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Ensuring HTTP exception is thrown when coffee id is not known.

    Args:
        dummy_coffees (DummyCoffees): The dummy coffees fixture.
        caplog (pytest.LogCaptureFixture): The log capture fixture.
    """

    unknown_id = uuid7()

    coffee_crud_mock = AsyncMock()
    coffee_crud_mock.delete.side_effect = ObjectNotFoundError("Test message")

    db_session_mock = AsyncMock()

    test_coffee_service = CoffeeService(coffee_crud=coffee_crud_mock)

    with pytest.raises(HTTPException) as http_error:
        await test_coffee_service.delete_coffee(
            db_session=db_session_mock, coffee_id=unknown_id
        )

    assert str(http_error.value.detail) == "No coffee found for given id"
