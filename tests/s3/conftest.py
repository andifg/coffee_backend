from typing import AsyncGenerator

import pytest
import pytest_asyncio
from minio import Minio  # type: ignore
from minio.commonconfig import ENABLED  # type: ignore
from minio.deleteobjects import DeleteObject  # type: ignore
from minio.error import S3Error  # type: ignore
from minio.versioningconfig import VersioningConfig  # type: ignore
from testcontainers.minio import MinioContainer  # type: ignore

from coffee_backend.settings import settings


@pytest.mark.usefixtures("patch_testcontainers_config")
@pytest_asyncio.fixture(name="minio_service", scope="session")
async def fixture_minio_service() -> AsyncGenerator[Minio, None]:
    """Creates a minio service for testing running in container."""

    with MinioContainer(
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
    ) as minio:
        test_client: Minio = minio.get_client()

        yield test_client


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
