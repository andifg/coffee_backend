from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.coffee import CoffeeService
from tests.conftest import DummyCoffees


@pytest.mark.asyncio
async def test_coffee_service_create(
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the create service method with a new coffee.

    This test verifies the behavior of the add_coffee method in the
    CoffeeService class when adding a new coffee object that does not already
    exist in the database.

    Args:
        dummy_coffees (DummyCoffees): A fixture providing dummy coffee objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """
    coffee_1 = dummy_coffees.coffee_1

    coffee_crud_mock = AsyncMock()
    coffee_crud_mock.create.return_value = coffee_1
    coffee_crud_mock.read.side_effect = ObjectNotFoundError("Just a test")

    db_session_mock = AsyncMock()

    test_coffee_service = CoffeeService(coffee_crud=coffee_crud_mock)

    result = await test_coffee_service.add_coffee(
        coffee=coffee_1, db_session=db_session_mock
    )
    coffee_crud_mock.create.assert_awaited_once_with(
        db_session=db_session_mock, coffee=coffee_1
    )

    assert result == coffee_1


@pytest.mark.asyncio
async def test_coffee_service_create_duplicate_name(
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the create service method with a duplicate coffee name.

    This test verifies the behavior of the add_coffee method in the
    CoffeeService class when attempting to add a new coffee with a name that
    already exists in the database.

    Args:
        dummy_coffees (DummyCoffees): A fixture providing dummy coffee objects.
        caplog (pytest.LogCaptureFixture): A fixture to capture log messages.
    """
    coffee_1 = dummy_coffees.coffee_1

    coffee_crud_mock = AsyncMock()
    coffee_crud_mock.create.return_value = coffee_1
    coffee_crud_mock.read.side_effect = [coffee_1]

    db_session_mock = AsyncMock()

    test_coffee_service = CoffeeService(coffee_crud=coffee_crud_mock)

    with pytest.raises(HTTPException) as http_error:
        await test_coffee_service.add_coffee(
            coffee=coffee_1, db_session=db_session_mock
        )

    assert (
        "Coffee with id 123e4567-e19b-12d3-a456-426655440000 will not get"
        " created due to name Colombian already existing" in caplog.messages
    )

    assert http_error.value.status_code == 400

    assert str(http_error.value.detail) == "Coffee name is already existing"
