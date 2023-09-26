from minio import Minio  # type: ignore

from coffee_backend.s3.types.readable import Readable
from coffee_backend.settings import settings


class ObjectCRUD:
    """Object CRUD operations."""

    def __init__(self, minio_client: Minio, bucket_name: str) -> None:
        """Initialize Object CRUD operations."""
        self.client = minio_client
        self.bucket_name = bucket_name

    def create(self, filename: str, file: Readable) -> None:
        """Create object in bucket."""
        result = self.client.put_object(
            self.bucket_name,
            f"{settings.minio_original_images_prefix}/{filename}",
            file,
            length=-1,
            part_size=10 * 1024 * 1024,
        )
        print(
            f"created {result.object_name} object; etag: {result.etag}, "
            + f"version-id: {result.version_id}"
        )
