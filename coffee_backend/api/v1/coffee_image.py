from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response
from motor.core import AgnosticClientSession

from coffee_backend.api.deps import (
    get_coffee_images_service,
    get_coffee_service,
)
from coffee_backend.mongo.database import get_db
from coffee_backend.services.coffee import CoffeeService
from coffee_backend.services.image_service import ImageService

router = APIRouter()


@router.post("/coffees/{coffee_id}/image")
async def _create_image(
    coffee_id: UUID,
    file: UploadFile = File(
        description='<img src="https://placebear.com/cache/395-205.jpg"'
        + ' alt="bear">'
    ),
    # object_crud: ObjectCRUD = Depends(get_object_crud),
    db_session: AgnosticClientSession = Depends(get_db),
    coffee_images_service: ImageService = Depends(get_coffee_images_service),
    coffee_service: CoffeeService = Depends(get_coffee_service),
) -> Response:
    """Upload a coffee image to the S3 bucket associated with a coffee.

    Args:
        coffee_id (UUID): The ID of the coffee associated with the image.
        file (UploadFile): The image file to upload.

    Returns:
        Response: A response indicating a successful upload (status code 201).

    Raises:
        HTTPException: If no file name is provided in the uploaded file.
    """

    await coffee_service.get_by_id(db_session=db_session, coffee_id=coffee_id)
    coffee_images_service.add_coffee_image(file, coffee_id)

    return Response(status_code=201)


@router.get(
    "/coffees/{coffee_id}/image",
    response_class=Response,
    response_model=bytes,
    responses={
        200: {
            "content": {"image/png": {}},
            "description": '<img src="https://placebear.com/cache/395-205.jpg"'
            + ' alt="bear">',
        },
        404: {"description": "Coffee image not found"},
    },
)
async def _get_image(
    coffee_id: UUID,
    coffee_images_service: ImageService = Depends(get_coffee_images_service),
) -> Response:
    """Retrieve a coffee image from the S3 bucket associated with a coffee.

    Args:
        coffee_id (UUID): The ID of the coffee associated with the image.

    Returns:
        Response: A response containing the coffee image.

    Raises:
        HTTPException: If the coffee image is not found in the S3 bucket.
    """

    image_bytes, filetype = coffee_images_service.get_coffee_image(coffee_id)

    return Response(
        content=image_bytes,
        media_type=f"image/{filetype}",
        headers={
            "Content-Disposition": "attachment; "
            + f"filename={coffee_id}.{filetype}"
        },
    )
