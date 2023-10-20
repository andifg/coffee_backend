from fastapi import APIRouter, Depends

from coffee_backend.api import health
from coffee_backend.api.security import VerifyToken
from coffee_backend.api.v1 import router as api_router
from coffee_backend.settings import settings

auth = VerifyToken(
    protocol=settings.keykloak_protocol,
    hostname=settings.keykloak_host,
    realm_name=settings.keykloak_realm,
    client_id=settings.keykloak_client_id,
)

router = APIRouter()
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(
    api_router, prefix="/api/v1", dependencies=[Depends(auth.verify)]
)
