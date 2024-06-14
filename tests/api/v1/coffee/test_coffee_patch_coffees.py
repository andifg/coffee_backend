import copy
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from uuid_extensions.uuid7 import uuid7

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas.coffee import UpdateCoffee
from tests.conftest import DummyCoffees, TestApp


@patch("coffee_backend.api.v1.coffees.authorize_coffee_edit_delete")
@patch("coffee_backend.services.coffee.CoffeeService.patch_coffee")
@pytest.mark.asyncio
async def test_api_patch_coffee(
    coffee_service_mock: AsyncMock,
    authorize_coffee_edit_delete_mock: MagicMock,
    test_app: TestApp,
    dummy_coffees: DummyCoffees,
    mock_security_dependency: Generator,
) -> None:
    """
    Test the PATCH /coffees/{id} API endpoint with a valid patch.

    Args:
        coffee_service_mock (AsyncMock): Mock object for the
            CoffeeService.patch_coffee method.
        test_app (TestApp): Test application instance.
        dummy_coffees (DummyCoffees): Fixture for dummy coffee objects.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True
    """

    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    authorize_coffee_edit_delete_mock.return_value = None

    unchanged_coffee = dummy_coffees.coffee_1

    updated_coffee = copy.deepcopy(unchanged_coffee)

    updated_coffee.name = "New updated name"

    update_coffee = UpdateCoffee(
        name="New updated name",
        roasting_company="Dalmayr",
        owner_id=unchanged_coffee.owner_id,
        owner_name=unchanged_coffee.owner_name,
    )

    coffee_jsonable = jsonable_encoder(update_coffee.dict(by_alias=True))

    coffee_service_mock.return_value = updated_coffee.dict(by_alias=True)

    response = await test_app.client.patch(
        f"/api/v1/coffees/{unchanged_coffee.id}",
        json=coffee_jsonable,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == jsonable_encoder(
        updated_coffee.dict(by_alias=True)
    )

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock,
        coffee_id=unchanged_coffee.id,
        update_coffee=update_coffee,
    )

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_api_patch_coffee_invalid_coffee_update_schema(
    test_app: TestApp,
    dummy_coffees: DummyCoffees,
    mock_security_dependency: Generator,
) -> None:
    """
    Test the PATCH /coffees/{id} API endpoint with an invalid coffee update
    schema.

    Ensure that updating ratings or ID fails.

    Args:
        test_app (TestApp): Test application instance.
        dummy_coffees (DummyCoffees): Fixture for dummy coffee objects.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True

    """
    coffee = dummy_coffees.coffee_1

    coffee_jsonable = jsonable_encoder(coffee.dict(by_alias=True))

    response = await test_app.client.patch(
        f"/api/v1/coffees/{coffee.id}",
        json=coffee_jsonable,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "_id"],
                "msg": "extra fields not permitted",
                "type": "value_error.extra",
            },
            {
                "loc": ["body", "rating_average"],
                "msg": "extra fields not permitted",
                "type": "value_error.extra",
            },
            {
                "loc": ["body", "rating_count"],
                "msg": "extra fields not permitted",
                "type": "value_error.extra",
            },
        ]
    }


@patch("coffee_backend.api.v1.coffees.authorize_coffee_edit_delete")
@patch("coffee_backend.services.coffee.CoffeeService.patch_coffee")
@pytest.mark.asyncio
async def test_api_patch_coffees_unknown_id(
    coffee_service_mock: AsyncMock,
    authorize_coffee_edit_delete_mock: MagicMock,
    test_app: TestApp,
    mock_security_dependency: Generator,
) -> None:
    """
    Test the PATCH /coffees/{id} API endpoint with an unknown coffee ID.

    Args:
        coffee_service_mock (AsyncMock): Mocked coffee service.
        test_app (TestApp): Test application instance.
        mock_security_dependency (Generator): Fixture to mock the authentication
            and authorization check within api to always return True

    Returns:
        None
    """
    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    authorize_coffee_edit_delete_mock.return_value = None

    coffee_service_mock.side_effect = HTTPException(
        status_code=404, detail="No coffees found"
    )

    unknown_id = uuid7()

    update_coffee = UpdateCoffee(
        name="New updated name",
        roasting_company="Dalmayr",
        owner_id=unknown_id,
        owner_name="Unknown owner",
    )

    coffee_jsonable = jsonable_encoder(update_coffee.dict(by_alias=True))

    response = await test_app.client.patch(
        f"/api/v1/coffees/{unknown_id}",
        json=coffee_jsonable,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "No coffees found"}

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock,
        coffee_id=unknown_id,
        update_coffee=update_coffee,
    )

    app.dependency_overrides = {}
