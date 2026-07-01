from app.models.health import HealthResponse


def get_health_status() -> HealthResponse:
    """Business logic for the health check.

    Trivial for now, but keeps the router thin and establishes the
    router -> service -> model pattern for future endpoints.
    """
    return HealthResponse(status="ok")
