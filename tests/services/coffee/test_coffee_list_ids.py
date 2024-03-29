from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.coffee import CoffeeService
from tests.conftest import DummyCoffees


@pytest.mark.asyncio
async def test_coffee_service_list_ids(
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the list ids coffee service method

    Args:
        dummy_coffees (DummyCoffees): A fixture providing dummy coffee objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """
    coffee_1 = dummy_coffees.coffee_1
    coffee_2 = dummy_coffees.coffee_2

    coffee_crud_mock = AsyncMock()
    coffee_crud_mock.read.return_value = [coffee_1, coffee_2]

    db_session_mock = AsyncMock()

    test_coffee_service = CoffeeService(coffee_crud=coffee_crud_mock)

    result = await test_coffee_service.list_ids(
        db_session=db_session_mock,
    )
    coffee_crud_mock.read.assert_awaited_once_with(
        db_session=db_session_mock,
        query={},
        projection={
            "_id": 1,
            "name": 1,
        },
    )

    assert result == [coffee_1.id, coffee_2.id]


@pytest.mark.asyncio
async def test_coffee_service_list_ids_with_empty_db_coffee_collection(
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the list service method.

    Args:
        dummy_coffees (DummyCoffees): A fixture providing dummy coffee objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """

    coffee_crud_mock = AsyncMock()
    coffee_crud_mock.read.side_effect = ObjectNotFoundError("Test message")

    db_session_mock = AsyncMock()

    test_coffee_service = CoffeeService(coffee_crud=coffee_crud_mock)

    with pytest.raises(HTTPException) as http_error:
        await test_coffee_service.list_ids(db_session=db_session_mock)

    assert str(http_error.value.detail) == "No ids found"
