from fastapi import APIRouter

from coffee_backend.schemas.health import HealthStatus

router = APIRouter()


@router.get(
    "",
    status_code=200,
    response_model=HealthStatus,
)
async def _get_health() -> HealthStatus:
    """Returns the health status of the coffee service.

    Returns:
        The health report.
    """
    return HealthStatus(healthy=True)
