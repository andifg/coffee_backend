"""Settings of the webservice."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """The settings used within the service

    Args:
        BaseSettings: The pydantic base settings that are automatically picking
            up environment variables and are matching those against the settings
            down below case insensitively.
    """

    build_version: str = "0.0.0"
    origins: list[str] = ["http://localhost:5173"]

    uvicorn_reload: bool = False

    host: str = "0.0.0.0"
    port: int = 8000

    log_level: str = "debug"

    mongodb_database: str = "coffee_backend"
    mongodb_coffee_collection: str = "coffee"
    mongodb_drink_collection: str = "drink"

    mongodb_host: str = "mongo"
    mongodb_port: int = 27017
    mongodb_username: str = "root"
    mongodb_password: str = "example"

    minio_host: str = "minio"
    minio_port: int = 9000

    minio_access_key: str = "minio-root-user"
    minio_secret_key: str = "minio-root-password"

    minio_original_images_prefix: str = "original"
    minio_coffee_images_bucket: str = "coffee-images"

    keykloak_host: str = "keycloak:8080"
    keykloak_protocol: str = "http"
    keycloak_issuer_host: str = "keycloak:8080"
    keykloak_issuer_protocol: str = "http"
    keykloak_realm: str = "Coffee-App"
    keykloak_client_id: str = "react-app"


settings = Settings()
