from fastapi import APIRouter

from app.models.health import HealthResponse
from app.services.health_service import get_health_status

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def read_health() -> HealthResponse:
    """Return the API health status."""
    return get_health_status()
