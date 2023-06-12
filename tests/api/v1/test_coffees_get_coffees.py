from unittest.mock import AsyncMock, patch

import pytest
from fastapi.encoders import jsonable_encoder

from coffee_backend.application import app
from coffee_backend.mongo.database import get_db
from tests.conftest import DummyCoffees, TestApp


@patch("coffee_backend.services.coffee.CoffeeService.list")
@pytest.mark.asyncio
async def test_api_get_coffees(
    coffee_service_mock: AsyncMock,
    test_app: TestApp,
    dummy_coffees: DummyCoffees,
) -> None:
    """Test coffees endpoint get mehtod."""

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

    coffee_service_mock.assert_awaited_once_with(db_session=get_db_mock)

    app.dependency_overrides = {}
