from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response
from motor.core import AgnosticClientSession

from coffee_backend.api.deps import (
    get_coffee_images_service,
    get_rating_service,
)
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas import CoffeeDrinkImage, ImageType
from coffee_backend.services.image_service import ImageService
from coffee_backend.services.rating import RatingService

router = APIRouter()


@router.post("/coffee-drink/{coffee_drink_id}/image")
async def _create_image(
    coffee_drink_id: UUID,
    file: UploadFile = File(
        description='<img src="https://placebear.com/cache/395-205.jpg"'
        + ' alt="bear">'
    ),
    db_session: AgnosticClientSession = Depends(get_db),
    image_service: ImageService = Depends(get_coffee_images_service),
    coffee_drink_service: RatingService = Depends(get_rating_service),
) -> Response:
    """Upload a coffee drink image associated with a coffee drink.

    Args:
        coffee_drink_id (UUID): The ID of the coffee drink associated with the
            image.
        file (UploadFile): The image file to upload.

    Returns:
        Response: A response indicating a successful upload (status code 201).

    Raises:
        HTTPException: If no file name is provided in the uploaded file.
    """

    await coffee_drink_service.get_by_id(db_session, coffee_drink_id)
    image_service.add_image(CoffeeDrinkImage(file=file, key=coffee_drink_id))

    return Response(status_code=201)


@router.get(
    "/coffee-drink/{coffee_drink_id}/image",
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
    coffee_drink_id: UUID,
    image_service: ImageService = Depends(get_coffee_images_service),
) -> Response:
    """Retrieve a coffee drink image associated with a coffee drink.

    Args:
        coffee_drink_id (UUID): The ID of the coffee drink associated with the
            image.

    Returns:
        Response: A response containing the coffee image.

    Raises:
        HTTPException: If the coffee image is not found in the S3 bucket.
    """

    image_bytes, filetype = image_service.get_image(
        object_id=coffee_drink_id, image_type=ImageType.COFFEE_DRINK
    )

    return Response(
        content=image_bytes,
        media_type=f"image/{filetype}",
        headers={
            "Content-Disposition": "attachment; "
            + f"filename={coffee_drink_id}.{filetype}"
        },
    )
