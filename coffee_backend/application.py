import logging

import motor.motor_asyncio  # type: ignore
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from coffee_backend.api import router
from coffee_backend.services.coffee import coffee_service
from coffee_backend.services.rating import rating_service
from coffee_backend.settings import settings

logging.basicConfig(level=logging.DEBUG)


origins: list[str] = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5173",
    "https://coffee-app.tests.apps.ocp4.gummy-bears.de",
]


# Initialize app
app = FastAPI(
    title="Coffee Backend -  API",
    docs_url="/api-docs",
    redoc_url=None,
)

app.state.mongodb_uri = (
    f"mongodb://{settings.mongodb_username}"
    f":{settings.mongodb_password}"
    f"@{settings.mongodb_host}:{settings.mongodb_port}"
)


app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    """Initializes the application and its processes."""
    logging.info("Starting up...")

    app.state.database_client = motor.motor_asyncio.AsyncIOMotorClient(
        app.state.mongodb_uri,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )

    app.state.coffee_service = coffee_service
    app.state.rating_service = rating_service


@app.on_event("shutdown")
async def shutdown() -> None:
    """Handles application shutdown and stops all processes gracefully."""

    logging.info("Shutting down...")
