from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from app import storage
from app.auth import CurrentUser
from app.schemas import UploadOut

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/images", response_model=UploadOut, status_code=201)
def upload_image(user: CurrentUser, file: Annotated[UploadFile, File()]):
    """Store a listing photo (JPEG, PNG or WebP, up to 4 MB) and return its key.

    Pass the key as `image` when creating a listing or service.
    """
    # Read one byte past the limit so an oversized file is detected without buffering all of it.
    data = file.file.read(storage.MAX_IMAGE_BYTES + 1)
    key = storage.store_image(user.id, data)
    return UploadOut(key=key, url=storage.public_url(key))
