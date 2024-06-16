import pytest

from coffee_backend.schemas.health import HealthStatus
from tests.conftest import TestApp


@pytest.mark.asyncio
async def test_health(test_app: TestApp) -> None:
    """Test health endpoint."""
    response = await test_app.client.get("/health")
    assert response.status_code == 200
    assert response.json() == HealthStatus(healthy=True).model_dump()
