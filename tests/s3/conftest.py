from typing import AsyncGenerator

import pytest_asyncio
from minio import Minio  # type: ignore
from minio.commonconfig import ENABLED  # type: ignore
from minio.deleteobjects import DeleteObject  # type: ignore
from minio.error import S3Error  # type: ignore
from minio.versioningconfig import VersioningConfig  # type: ignore
from pytest_docker.plugin import Services  # type: ignore

from coffee_backend.settings import settings


@pytest_asyncio.fixture(name="minio_service")
async def fixture_minio_service(
    docker_ip: str, docker_services: Services
) -> Minio:
    """Ensure that HTTP service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("minio", 9000)
    connection_string = f"{docker_ip}:{port}"
    test_client = Minio(
        connection_string,
        settings.minio_access_key,
        settings.minio_secret_key,
        secure=False,
    )
    print(connection_string)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: test_minio(test_client)
    )
    return test_client


@pytest_asyncio.fixture()
async def init_minio(minio_service: Minio) -> AsyncGenerator:
    """Create sync connection to minio for testing.

    Args:
        minio_service: Fixture for checking availability of mongo db

    Yields:
        TestDBSessions object with sync and asnyc session
    """

    try:
        minio_service.make_bucket(settings.minio_coffee_images_bucket)

    except S3Error as e:
        if e.code == "BucketAlreadyOwnedByYou":
            pass
        else:
            raise e

    minio_service.set_bucket_versioning(
        settings.minio_coffee_images_bucket, VersioningConfig(ENABLED)
    )
    yield minio_service
    cleanup_minio(minio_service)


def test_minio(test_client: Minio) -> bool:
    """Test if sync connection can be astablished.

    Args:
        connection_string: minio connection string

    Returns:
        Return true if no error occured
    """
    print("Try connection")
    test_client.list_buckets()
    return True


def cleanup_minio(minio_client: Minio) -> None:
    """Drop bucket inbetween tests.

    Args:
        minio_client: Minio client
    """

    delete_object_list = [
        DeleteObject(object.object_name, object.version_id)
        for object in minio_client.list_objects(
            "coffee-images", "original/", recursive=True, include_version=True
        )
    ]

    delete_generator = minio_client.remove_objects(
        "coffee-images", delete_object_list
    )

    for deletion in delete_generator:
        print("error occurred when deleting object", deletion)

    minio_client.remove_bucket(settings.minio_coffee_images_bucket)
    print("Cleaned up minio between tests")
