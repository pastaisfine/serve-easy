from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Pooled Neon connection, used by the API at runtime.
    database_url: str
    # Direct Neon connection, used by migrations and seeding. Falls back to the pooled URL.
    database_url_unpooled: str | None = None

    # Only the photo-fetch script needs this; the API and seed do not.
    unsplash_access_key: str | None = None

    # Neon Auth (Managed Better Auth). The frontend forwards a short-lived JWT and
    # the API verifies it against the JWKS. Unset => every authenticated route answers 503.
    neon_auth_base_url: str | None = None
    neon_auth_jwks_url: str | None = None

    # Neon Object Storage (S3-compatible, path-style). Names follow the AWS convention
    # that `neon env pull` writes. Unset => uploads answer 503.
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_endpoint_url_s3: str | None = None
    aws_region: str | None = None
    storage_bucket: str = "uploads"

    # Telegram bot. Set => the bot starts with the API and answers with
    # read-only queries against the same database. Unset => no bot.
    telegram_bot_token: str | None = None

    @property
    def migration_url(self) -> str:
        return self.database_url_unpooled or self.database_url


def to_sqlalchemy_url(url: str) -> str:
    """Neon gives `postgresql://` URLs; force the psycopg (v3) driver."""
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]
    return url


settings = Settings()  # type: ignore[call-arg]
