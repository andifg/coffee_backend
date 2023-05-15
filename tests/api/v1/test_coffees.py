import pytest
from fastapi.encoders import jsonable_encoder

from tests.conftest import DummyCoffees, TestApp


@pytest.mark.asyncio
async def test_api_create_coffee(
    test_app: TestApp, dummy_coffees: DummyCoffees
) -> None:
    """Test health endpoint."""

    coffee = dummy_coffees.coffee_1

    coffee_jsonable = jsonable_encoder(coffee.dict(by_alias=True))

    response = await test_app.client.post(
        "/api/v1/coffees/",
        json=coffee_jsonable,
        headers={"Content-Type": "application/json"},
    )

    print(response.json())

    assert response.status_code == 201
    assert response.json() == coffee_jsonable
