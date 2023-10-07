from typing import Tuple

from minio import Minio  # type: ignore
from minio import S3Error  # type: ignore

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.s3.types.readable import Readable
from coffee_backend.settings import settings


class ObjectCRUD:
    """Class for performing CRUD operations on objects in an S3 bucket."""

    def __init__(self, minio_client: Minio, bucket_name: str) -> None:
        """Initialize ObjectCRUD operations.

        Args:
            minio_client (Minio): The Minio client instance.
            bucket_name (str): The name of the S3 bucket to use for CRUD
                operations.

        """
        self.client = minio_client
        self.bucket_name = bucket_name

    def create(self, filename: str, file: Readable, file_type: str) -> None:
        """Create an object in the S3 bucket.

        Args:
            filename (str): The name of the object to be created.
            file (Readable): The content of the object to be uploaded.
            file_type (str): The type of the file, used as metadata.

        Returns:
            None

        """
        result = self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=f"{settings.minio_original_images_prefix}/{filename}",
            data=file,
            length=-1,
            part_size=10 * 1024 * 1024,
            metadata={"filetype": file_type},
        )
        print(
            f"created {result.object_name} object; etag: {result.etag}, "
            + f"version-id: {result.version_id}"
        )

    def read(self, filename: str) -> Tuple[bytes, str]:
        """Read an object from the S3 bucket.

        Args:
            filename (str): The name of the object to be read.

        Returns:
            Tuple[bytes, str]: A tuple containing the object data (bytes) and
                its file type.

        Raises:
            ObjectNotFoundError: If the specified object does not exist.
            Exception: If an error occurs while interacting with the S3 bucket.

        """
        try:
            result = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=f"{settings.minio_original_images_prefix}/"
                + filename,
            )
        except S3Error as error:
            if error.code == "NoSuchKey":
                raise ObjectNotFoundError("Object not found") from error
            raise error

        filetype = result.headers.get("x-amz-meta-filetype", "")

        return result.data, filetype
