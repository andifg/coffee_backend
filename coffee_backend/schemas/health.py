from pydantic import BaseModel


class HealthStatus(BaseModel):
    """Health endpoint schema."""

    healthy: bool
