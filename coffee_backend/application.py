import logging

from fastapi import FastAPI

from coffee_backend.api import router

logging.basicConfig(level=logging.DEBUG)


# Initialize app
app = FastAPI(
    title="Coffee Backend -  API",
    docs_url="/api-docs",
    redoc_url=None,
)


app.include_router(router)


@app.on_event("startup")
async def startup() -> None:
    """Initializes the application and its processes."""
    logging.info("Starting up...")


@app.on_event("shutdown")
async def shutdown() -> None:
    """Handles application shutdown and stops all processes gracefully."""

    logging.info("Shutting down...")
