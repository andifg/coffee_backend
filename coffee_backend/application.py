import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import motor.motor_asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from minio import Minio  # type: ignore

from coffee_backend.api import router
from coffee_backend.config.log_levels import log_levels
from coffee_backend.s3.object import ObjectCRUD
from coffee_backend.services.coffee import coffee_service
from coffee_backend.services.drink import drink_service
from coffee_backend.services.image_service import ImageService
from coffee_backend.settings import settings

logging.basicConfig(level=log_levels.get(settings.log_level, logging.INFO))


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Initializes the application and its processes."""
    logging.info("Starting up...")
    logging.info("Log level is %s", logging.getLogger().level)
    logging.debug("Debug logging is enabled")

    application.state.database_client = motor.motor_asyncio.AsyncIOMotorClient(
        app.state.mongodb_uri,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )

    application.state.coffee_images_service = ImageService(
        object_crud=ObjectCRUD(
            minio_client=Minio(
                f"{settings.minio_host}:{settings.minio_port}",
                settings.minio_access_key,
                settings.minio_secret_key,
                secure=False,
            ),
            bucket_name=settings.minio_coffee_images_bucket,
        )
    )
    application.state.coffee_service = coffee_service
    application.state.drink_service = drink_service

    yield

    logging.info("Shutting down...")


# Initialize app
app = FastAPI(
    title="Coffee Backend -  API",
    docs_url="/api-docs",
    redoc_url=None,
    lifespan=lifespan,
)

app.state.mongodb_uri = (
    f"mongodb://{settings.mongodb_username}"
    f":{settings.mongodb_password}"
    f"@{settings.mongodb_host}:{settings.mongodb_port}"
)


app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
