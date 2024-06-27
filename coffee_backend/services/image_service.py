import logging
from typing import Tuple
from uuid import UUID

from fastapi import HTTPException

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.s3.object import ObjectCRUD
from coffee_backend.schemas import ImageType, S3Object


class ImageService:
    """Service layer between the API and CRUD layer for handling all image
    related operations.
    """

    def __init__(self, object_crud: ObjectCRUD):
        """Initialize the ImageService.

        Args:
            object_crud (ObjectCRUD): An instance of the ObjectCRUD
                class for managing image objects.

        """
        self.object_crud = object_crud

    def add_image(self, s3_object: S3Object) -> None:
        """Add a coffee image to the S3 bucket associated with a coffee.

        Args:
            coffee_image (UploadFile): The coffee image to be added.
            coffee_id (UUID): The ID of the coffee associated with the image.

        Raises:
            HTTPException: If no file name is provided in the coffee_image.

        """

        if not s3_object.file.content_type:
            raise HTTPException(
                status_code=400, detail="No content type provided"
            )

        filetype = s3_object.file.content_type.split("/")[1]

        self.object_crud.create(
            filepath=s3_object.context_path + "/" + "original",
            filename=str(s3_object.key),
            file=s3_object.file.file,
            file_type=filetype,
        )

        logging.debug(
            "Added object %s with key %s", s3_object.type.value, s3_object.key
        )

    def get_image(
        self, object_id: UUID, image_type: ImageType
    ) -> Tuple[bytes, str]:
        """Retrieve if existing small, otherwise original image from S3.

        Try to get the small version of the image, if it does not exist, get the
        original version.

        Args:
            coffee_id (UUID): The ID of the coffee associated with the image.

        Returns:
            Tuple[bytes, str]: A tuple containing the coffee image data (bytes)
                and its file type.

        Raises:
            HTTPException: If the coffee image is not found in the S3 bucket.

        """
        try:
            return self.object_crud.read(
                filepath=f"{image_type.value}/small", filename=str(object_id)
            )
        except ObjectNotFoundError:
            logging.debug(
                "No small image found for %s with id %s", image_type, object_id
            )

            try:
                return self.object_crud.read(
                    filepath=f"{image_type.value}/original",
                    filename=str(object_id),
                )

            except ObjectNotFoundError as exception:
                logging.debug(
                    "No original image found for %s with id %s",
                    image_type,
                    object_id,
                )
                raise HTTPException(
                    status_code=404, detail=f"{image_type} Image not found"
                ) from exception

    def delete_image(self, object_id: UUID, image_type: ImageType) -> None:
        """Delete all images from the S3 bucket associated with an object id.

        Delete both the small and original versions of the image.

        Args:
            object_id (UUID): The ID of the object associated with the image.
        """
        self.object_crud.delete(
            filepath=f"{image_type.value}/small", filename=str(object_id)
        )
        self.object_crud.delete(
            filepath=f"{image_type.value}/original", filename=str(object_id)
        )

        logging.debug(
            "Deleted all versions for %s image with id %s",
            image_type.value,
            object_id,
        )
