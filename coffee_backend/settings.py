"""Settings of the webservice."""
from __future__ import annotations

from pydantic import BaseSettings


class Settings(BaseSettings):
    """The settings used within the service

    Args:
        BaseSettings: The pydantic base settings that are automatically picking
            up environment variables and are matching those against the settings
            down below case insensitively.
    """

    build_version: str = "0.0.0"

    host: str = "0.0.0.0"
    port: int = 8000

    log_level: str = "info"

    mongodb_database: str = "coffee_backend"
    mongodb_coffee_collection: str = "coffee"
    mongodb_rating_collection: str = "rating"

    mongodb_host: str = "localhost"
    mongodb_port: int = 27017
    mongodb_username: str = "root"
    mongodb_password: str = "example"

    minio_host: str = "localhost"
    minio_port: int = 9000

    minio_access_key: str = "minio-root-user"
    minio_secret_key: str = "minio-root-password"

    minio_original_images_prefix: str = "original"
    minio_coffee_images_bucket: str = "coffee-images"

    keykloak_host: str = "localhost:8080"
    keykloak_realm: str = "Coffee-App"
    keykloak_protocol: str = "http"
    keykloak_client_id: str = "react-app"


settings = Settings()
