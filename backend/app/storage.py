"""Image storage on Neon Object Storage (S3-compatible).

The database stores the object *key* (for example ``listings/<user>/<uuid>.jpg``),
never a URL. The key is turned into a URL on the way out (`public_url`), because the
storage endpoint is per Neon branch and a branch copy must not point at its parent's host.
"""

import uuid
from functools import lru_cache

import boto3
from botocore.config import Config
from fastapi import HTTPException

from app.config import settings

MAX_IMAGE_BYTES = 4 * 1024 * 1024  # Keep under the 4.5MB request limit of common hosts.

# Detect the type from the bytes, never from the client's Content-Type or filename.
_SIGNATURES: tuple[tuple[bytes, str, str], ...] = (
    (b"\xff\xd8\xff", "image/jpeg", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "image/png", "png"),
)

KEY_PREFIX = "listings"


def detect_image_type(data: bytes) -> tuple[str, str] | None:
    """Return (content_type, extension) for a JPEG, PNG or WebP, else None."""
    for magic, content_type, ext in _SIGNATURES:
        if data.startswith(magic):
            return content_type, ext
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp", "webp"
    return None


def is_storage_configured() -> bool:
    return bool(
        settings.aws_access_key_id
        and settings.aws_secret_access_key
        and settings.aws_endpoint_url_s3
    )


@lru_cache(maxsize=1)
def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.aws_endpoint_url_s3,
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        # Neon requires path-style addressing and SigV4.
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def key_belongs_to(key: str, user_id: str) -> bool:
    """Whether `key` is an upload made by `user_id`, so users can't attach someone else's photo."""
    return key.startswith(f"{KEY_PREFIX}/{user_id}/") and ".." not in key


def store_image(user_id: str, data: bytes) -> str:
    """Validate and upload an image, returning its object key."""
    if not is_storage_configured():
        raise HTTPException(503, "Image storage is not configured")
    if not data:
        raise HTTPException(400, "The file is empty")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(413, f"Images can be at most {MAX_IMAGE_BYTES // (1024 * 1024)} MB")
    detected = detect_image_type(data)
    if detected is None:
        raise HTTPException(415, "Only JPEG, PNG or WebP images are allowed")
    content_type, ext = detected

    key = f"{KEY_PREFIX}/{user_id}/{uuid.uuid4()}.{ext}"
    _client().put_object(
        Bucket=settings.storage_bucket,
        Key=key,
        Body=data,
        ContentType=content_type,
        # Keys are unique per upload and never overwritten, so caches may hold them forever.
        CacheControl="public, max-age=31536000, immutable",
    )
    return key


def delete_image(key: str) -> None:
    _client().delete_object(Bucket=settings.storage_bucket, Key=key)


def public_url(image: str | None) -> str | None:
    """Resolve a stored value to a URL.

    Seeded rows hold full http(s) URLs (Unsplash, placehold.co) and pass through
    unchanged; uploads hold an object key in the public-read bucket.
    """
    if not image:
        return None
    if image.startswith(("http://", "https://")):
        return image
    return f"{settings.aws_endpoint_url_s3}/{settings.storage_bucket}/{image}"
