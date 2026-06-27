from functools import cached_property
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "University Knowledge Search"
    app_env: str = "local"
    api_v1_prefix: str = "/api/v1"
    max_upload_size_bytes: int = 20 * 1024 * 1024
    upload_dir: Path = Path("uploads")
    chunk_size: int = 1000
    chunk_overlap: int = 100
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "documents"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "knowledge_search"
    postgres_user: str = "knowledge_user"
    postgres_password: str = Field(default="knowledge_password", repr=False)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @cached_property
    def database_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
