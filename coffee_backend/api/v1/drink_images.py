from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response
from motor.core import AgnosticClientSession

from coffee_backend.api.deps import get_coffee_images_service, get_drink_service
from coffee_backend.mongo.database import get_db
from coffee_backend.schemas import CoffeeDrinkImage, ImageType
from coffee_backend.services.drink import DrinkService
from coffee_backend.services.image_service import ImageService

router = APIRouter()


@router.post("/drinks/{drink_id}/image")
async def _create_image(
    drink_id: UUID,
    file: UploadFile = File(
        description='<img src="https://placebear.com/cache/395-205.jpg"'
        + ' alt="bear">'
    ),
    db_session: AgnosticClientSession = Depends(get_db),
    image_service: ImageService = Depends(get_coffee_images_service),
    coffee_drink_service: DrinkService = Depends(get_drink_service),
) -> Response:
    """Upload a coffee drink image associated with a coffee drink.

    Args:
        drink_id (UUID): The ID of the drink associated with the
            image.
        file (UploadFile): The image file to upload.

    Returns:
        Response: A response indicating a successful upload (status code 201).

    Raises:
        HTTPException: If no file name is provided in the uploaded file.
    """

    await coffee_drink_service.get_by_id(db_session, drink_id)
    image_service.add_image(CoffeeDrinkImage(file=file, key=drink_id))

    return Response(status_code=201)


@router.get(
    "/drinks/{drink_id}/image",
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
    drink_id: UUID,
    image_service: ImageService = Depends(get_coffee_images_service),
) -> Response:
    """Retrieve a coffee drink image associated with a coffee drink.

    Args:
        drink_id (UUID): The ID of the drink associated with the
            image.

    Returns:
        Response: A response containing the coffee image.

    Raises:
        HTTPException: If the coffee image is not found in the S3 bucket.
    """

    image_bytes, filetype = image_service.get_image(
        object_id=drink_id, image_type=ImageType.COFFEE_DRINK
    )

    return Response(
        content=image_bytes,
        media_type=f"image/{filetype}",
        headers={
            "Content-Disposition": "attachment; "
            + f"filename={drink_id}.{filetype}"
        },
    )
