from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    bot_token: str = Field(alias="BOT_TOKEN")
    admin_id: int = Field(alias="ADMIN_ID")
    admin_username: str = Field(default="admin_username", alias="ADMIN_USERNAME")

    @field_validator("admin_username")
    @classmethod
    def sanitize_username(cls, v: str) -> str:
        return v.lstrip("@")

    database_url: str = Field(
        default="sqlite+aiosqlite:///data/planner.db", alias="DATABASE_URL"
    )
    redis_url: str | None = Field(default=None, alias="REDIS_URL")

    default_timezone: str = Field(default="Asia/Tashkent", alias="DEFAULT_TIMEZONE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    trial_days: int = Field(default=3, alias="TRIAL_DAYS")
    sentry_dsn: str | None = Field(default=None, alias="SENTRY_DSN")

    ai_provider: str | None = Field(default=None, alias="AI_PROVIDER")
    ai_api_key: str | None = Field(default=None, alias="AI_API_KEY")


@lru_cache
def get_settings() -> Settings:
    return Settings()
