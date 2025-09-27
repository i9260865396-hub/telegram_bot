from __future__ import annotations

from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env files."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(default="", alias="BOT_TOKEN")
    database_url: str = Field(default="sqlite+aiosqlite:///./bot.db", alias="DATABASE_URL")
    admin_ids: List[int] = Field(default_factory=list, alias="ADMIN_IDS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    AI_ENABLED: bool = Field(default=False)
    NOTIFY_ENABLED: bool = Field(default=True)
    WORKDAY_END_HOUR: int = Field(default=16)
    TIMEZONE: str = Field(default="Europe/Vilnius")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: object) -> List[int]:
        if value is None:
            return []
        if isinstance(value, str):
            parts = [item.strip() for item in value.split(",")]
            return [int(item) for item in parts if item]
        if isinstance(value, (list, tuple, set)):
            return [int(item) for item in value]
        raise TypeError("ADMIN_IDS must be provided as a comma-separated string or an iterable of integers")

    def get_admin_ids(self) -> List[int]:
        """Return a list of administrator IDs as integers."""

        return list(self.admin_ids)


settings = Settings()
