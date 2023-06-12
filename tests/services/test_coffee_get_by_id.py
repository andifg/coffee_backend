from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.coffee import CoffeeService
from tests.conftest import DummyCoffees


@pytest.mark.asyncio
async def test_coffee_service_get_by_id(
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the get_by_id coffee service method

    Args:
        dummy_coffees (DummyCoffees): A fixture providing dummy coffee objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """
    coffee_1 = dummy_coffees.coffee_1

    coffee_crud_mock = AsyncMock()
    coffee_crud_mock.read.return_value = [coffee_1]

    db_session_mock = AsyncMock()

    test_coffee_service = CoffeeService(coffee_crud=coffee_crud_mock)

    result = await test_coffee_service.get_by_id(
        db_session=db_session_mock, coffee_id=coffee_1.id
    )
    coffee_crud_mock.read.assert_awaited_once_with(
        db_session=db_session_mock, query={"_id": coffee_1.id}
    )

    assert result == coffee_1


@pytest.mark.asyncio
async def test_coffee_service_get_by_id_with_unknown_id(
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the list service method.

    Args:
        dummy_coffees (DummyCoffees): A fixture providing dummy coffee objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """
    unknown_id = uuid7()

    coffee_crud_mock = AsyncMock()
    coffee_crud_mock.read.side_effect = ObjectNotFoundError("Test message")

    db_session_mock = AsyncMock()

    test_coffee_service = CoffeeService(coffee_crud=coffee_crud_mock)

    with pytest.raises(HTTPException) as http_error:
        await test_coffee_service.get_by_id(
            db_session=db_session_mock, coffee_id=unknown_id
        )

    assert str(http_error.value.detail) == "No coffee found for given id"
