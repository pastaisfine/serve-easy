from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Pooled Neon connection, used by the API at runtime.
    database_url: str
    # Direct Neon connection, used by migrations and seeding. Falls back to the pooled URL.
    database_url_unpooled: str | None = None

    # Only the photo-fetch script needs this; the API and seed do not.
    unsplash_access_key: str | None = None

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
