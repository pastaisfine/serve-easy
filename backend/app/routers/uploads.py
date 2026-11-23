from typing import Annotated, Literal

from fastapi import APIRouter, File, Query, UploadFile

from app import storage
from app.auth import CurrentUser
from app.schemas import UploadOut

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/images", response_model=UploadOut, status_code=201)
def upload_image(
    user: CurrentUser,
    file: Annotated[UploadFile, File()],
    purpose: Annotated[Literal["listing", "meal"], Query()] = "listing",
):
    """Store a listing photo (JPEG, PNG or WebP, up to 4 MB) and return its key.

    Pass the key as `image` when creating a listing or service.
    """
    # Read one byte past the limit so an oversized file is detected without buffering all of it.
    data = file.file.read(storage.MAX_IMAGE_BYTES + 1)
    namespace = storage.MEAL_KEY_PREFIX if purpose == "meal" else storage.KEY_PREFIX
    key = storage.store_image(user.id, data, namespace=namespace)
    return UploadOut(key=key, url=storage.public_url(key))
