from fastapi import Depends, FastAPI, File, UploadFile
from fastapi.responses import Response

from coffee_backend.api.deps import get_object_crud
from coffee_backend.s3.object import ObjectCRUD

app = FastAPI()


@app.post("/coffees/{coffee_id}/images")
async def create_file(
    file: UploadFile = File(...),
    object_crud: ObjectCRUD = Depends(get_object_crud),
) -> Response:
    """_summary_

    Args:
        file: _description_. Defaults to File(...).
        object_crud: _description_. Defaults to Depends(get_object_crud).

    Returns:
        _description_
    """
    if not file.filename:
        return Response(status_code=400, content="No file name")

    object_crud.create(file.filename, file.file)

    return Response(status_code=201)
