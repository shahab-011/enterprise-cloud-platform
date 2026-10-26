from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Enterprise Cloud Platform Modernization Demo"
    database_path: str = "data/platform.sqlite3"
    database_timeout_seconds: float = Field(default=5.0, gt=0, le=60)
    rate_limit_requests: int = Field(default=60, ge=1, le=10000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3600)
