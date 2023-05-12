import uvicorn

from coffee_backend.settings import settings


def main() -> None:
    """Start uvicorn programmatically."""
    uvicorn.run(
        "coffee_backend.application:app",
        host=settings.host,
        port=settings.port,
        log_level=None,
        log_config=None,
    )


def init() -> None:
    """Makes the entrypoint callable for testing."""
    if __name__ == "__main__":
        main()


init()
