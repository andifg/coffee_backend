import copy
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from uuid_extensions.uuid7 import uuid7

from coffee_backend.schemas.coffee import UpdateCoffee
from coffee_backend.services.coffee import CoffeeService
from tests.conftest import DummyCoffees


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@pytest.mark.asyncio
async def test_coffee_service_patch(
    get_by_id_mock: AsyncMock,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test the patch_coffee method of the CoffeeService class with valid patch.

    Args:
        get_by_id_mock (AsyncMock): Mocked get_by_id method.
        dummy_coffees (DummyCoffees): Fixture providing dummy coffee objects.
        caplog (pytest.LogCaptureFixture): Fixture to capture log messages.
    """
    unchanged_coffee = dummy_coffees.coffee_1

    updated_coffee = copy.deepcopy(unchanged_coffee)

    updated_coffee.name = "Super cool new name"
    updated_coffee.roasting_company = "Dalmayr"

    update_coffee = UpdateCoffee(
        name="Super cool new name",
        roasting_company="Dalmayr",
        owner_id=unchanged_coffee.owner_id,
        owner_name=unchanged_coffee.owner_name,
    )

    get_by_id_mock.return_value = unchanged_coffee

    coffee_crud_mock = AsyncMock()
    coffee_crud_mock.update.return_value = updated_coffee

    db_session_mock = AsyncMock()

    test_coffee_service = CoffeeService(coffee_crud=coffee_crud_mock)

    result = await test_coffee_service.patch_coffee(
        db_session=db_session_mock,
        coffee_id=unchanged_coffee.id,
        update_coffee=update_coffee,
    )
    coffee_crud_mock.update.assert_awaited_once_with(
        db_session=db_session_mock,
        coffee=updated_coffee,
        coffee_id=unchanged_coffee.id,
    )

    assert result == updated_coffee


@patch("coffee_backend.services.coffee.CoffeeService.get_by_id")
@pytest.mark.asyncio
async def test_coffee_service_patch_invalid_id(
    get_by_id_mock: AsyncMock,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test the patch_coffee method of the CoffeeService class with an invalid
    coffee ID.

    Args:
        get_by_id_mock (AsyncMock): Mocked get_by_id method.
        dummy_coffees (DummyCoffees): Fixture providing dummy coffee objects.
        caplog (pytest.LogCaptureFixture): Fixture to capture log messages.
    """

    unknown_id = uuid7()
    update_coffee = UpdateCoffee(
        name="New updated name",
        roasting_company="Dalmayr",
        owner_id=uuid7(),
        owner_name="Unknown owner",
    )

    db_session_mock = AsyncMock()
    coffee_crud_mock = AsyncMock()

    get_by_id_mock.side_effect = HTTPException(
        status_code=404, detail="No coffee found for given id"
    )

    update_coffee = UpdateCoffee(
        name="Super cool new name",
        roasting_company="Dalmayr",
        owner_id=uuid7(),
        owner_name="Unknown owner",
    )

    test_coffee_service = CoffeeService(coffee_crud=coffee_crud_mock)

    with pytest.raises(HTTPException) as http_error:
        await test_coffee_service.patch_coffee(
            db_session=db_session_mock,
            coffee_id=unknown_id,
            update_coffee=update_coffee,
        )

    assert http_error.value.status_code == 404

    assert str(http_error.value.detail) == "No coffee found for given id"
