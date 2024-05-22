from typing import Generator
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyCoffees, TestApp


@patch(
    "coffee_backend.services.coffee.CoffeeService.list_coffees_with_rating_summary"
)
@pytest.mark.asyncio
async def test_api_get_coffees(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_coffees: DummyCoffees,
    mock_security_dependency: Generator,
) -> None:
    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.return_value = [
        dummy_coffees.coffee_1.dict(by_alias=True),
        dummy_coffees.coffee_2.dict(by_alias=True),
    ]

    response = await test_app.client.get(
        "/api/v1/coffees",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == [
        jsonable_encoder(dummy_coffees.coffee_1.dict(by_alias=True)),
        jsonable_encoder(dummy_coffees.coffee_2.dict(by_alias=True)),
    ]

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock,
        page=1,
        page_size=10,
        owner_id=None,
        first_id=None,
    )

    app.dependency_overrides = {}


@patch(
    "coffee_backend.services.coffee.CoffeeService.list_coffees_with_rating_summary"
)
@pytest.mark.asyncio
async def test_api_get_coffees_with_emtpy_crud_response(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    mock_security_dependency: Generator,
) -> None:
    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.side_effect = HTTPException(
        status_code=404, detail="No coffees found"
    )

    response = await test_app.client.get(
        "/api/v1/coffees",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "No coffees found"}

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock,
        page=1,
        page_size=10,
        owner_id=None,
        first_id=None,
    )

    app.dependency_overrides = {}


@patch(
    "coffee_backend.services.coffee.CoffeeService.list_coffees_with_rating_summary"
)
@pytest.mark.asyncio
async def test_api_get_coffees_with_query_params(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_coffees: DummyCoffees,
    mock_security_dependency: Generator,
) -> None:
    get_db_mock = AsyncMock()

    app.dependency_overrides[get_db] = lambda: get_db_mock

    coffee_service_mock.return_value = [
        dummy_coffees.coffee_1.dict(by_alias=True),
        dummy_coffees.coffee_2.dict(by_alias=True),
    ]

    response = await test_app.client.get(
        "/api/v1/coffees?page=1&page_size=10&owner_id=12345678-1234-5678-1234-567812345678&first_id=123e4567-e19b-12d3-a456-426655440000",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == [
        jsonable_encoder(dummy_coffees.coffee_1.dict(by_alias=True)),
        jsonable_encoder(dummy_coffees.coffee_2.dict(by_alias=True)),
    ]

    coffee_service_mock.assert_awaited_once_with(
        db_session=get_db_mock,
        page=1,
        page_size=10,
        owner_id=UUID("12345678-1234-5678-1234-567812345678"),
        first_id=UUID("123e4567-e19b-12d3-a456-426655440000"),
    )

    app.dependency_overrides = {}
