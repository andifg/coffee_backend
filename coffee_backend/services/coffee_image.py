import logging
import os
from typing import Tuple
from uuid import UUID

from fastapi import HTTPException, UploadFile

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.s3.object import ObjectCRUD


class ImageService:
    """Service layer between the API and CRUD layer for handling coffee-images
    related operations.
    """

    def __init__(self, coffee_images_crud: ObjectCRUD):
        """Initialize the CoffeeImagesService.

        Args:
            coffee_images_crud (ObjectCRUD): An instance of the ObjectCRUD
                class for managing coffee image objects.

        """
        self.coffee_images_crud = coffee_images_crud

    def add_coffee_image(
        self, coffee_image: UploadFile, coffee_id: UUID
    ) -> None:
        """Add a coffee image to the S3 bucket associated with a coffee.

        Args:
            coffee_image (UploadFile): The coffee image to be added.
            coffee_id (UUID): The ID of the coffee associated with the image.

        Raises:
            HTTPException: If no file name is provided in the coffee_image.

        """

        if not coffee_image.filename:
            raise HTTPException(status_code=400, detail="No file name provided")

        filetype = os.path.splitext(coffee_image.filename)[1]
        filetype = filetype.lstrip(".")

        self.coffee_images_crud.create(
            str(coffee_id), coffee_image.file, filetype
        )

        logging.debug("Added coffee image for coffee with id %s", coffee_id)

    def get_coffee_image(self, coffee_id: UUID) -> Tuple[bytes, str]:
        """Retrieve a coffee image from the S3 bucket associated with a coffee.

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
            return self.coffee_images_crud.read(str(coffee_id), "small")
        except ObjectNotFoundError:
            logging.debug(
                "No small image found for coffee with id %s", coffee_id
            )

            try:
                return self.coffee_images_crud.read(str(coffee_id), "original")

            except ObjectNotFoundError as exception:
                logging.debug(
                    "No original image found for coffee with id %s", coffee_id
                )
                raise HTTPException(
                    status_code=404, detail="Coffee image not found"
                ) from exception

    def delete_coffee_image(self, coffee_id: UUID) -> None:
        """Delete all coffee images from the S3 bucket associated with a coffee.

        Delete both the small and original versions of the image.

        Args:
            coffee_id (UUID): The ID of the coffee associated with the image.
        """
        self.coffee_images_crud.delete(str(coffee_id), "small")
        self.coffee_images_crud.delete(str(coffee_id), "original")

        logging.debug(
            "Deleted all versions for coffee image for coffee with id %s",
            coffee_id,
        )
