from typing import AsyncGenerator

import pytest_asyncio
from minio import Minio  # type: ignore
from minio.commonconfig import ENABLED  # type: ignore
from minio.deleteobjects import DeleteObject  # type: ignore
from minio.error import S3Error  # type: ignore
from minio.versioningconfig import VersioningConfig  # type: ignore
from testcontainers.core.container import DockerContainer  # type: ignore
from testcontainers.core.waiting_utils import wait_for  # type: ignore

from coffee_backend.settings import settings


@pytest_asyncio.fixture(name="minio_service", scope="session")
async def fixture_minio_service(
    _init_testcontainer: None,
) -> AsyncGenerator[Minio, None]:
    """Creates a minio service for testing running in container."""

    minio_testcontainer = (
        DockerContainer(image="bitnami/minio:2024.3.5")
        .with_exposed_ports(9000)
        .with_env("MINIO_ROOT_USER", settings.minio_access_key)
        .with_env("MINIO_ROOT_PASSWORD", settings.minio_secret_key)
    )

    with minio_testcontainer as container:
        host_ip = container.get_container_host_ip()
        exposed_port = container.get_exposed_port(9000)
        minio = Minio(
            f"{host_ip}:{exposed_port}",
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False,
        )
        wait_for(lambda: test_minio(minio))
        yield minio


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
    try:
        test_client.list_buckets()
    except S3Error as e:
        print(e)
        return False
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
