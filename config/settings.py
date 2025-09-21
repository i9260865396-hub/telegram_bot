from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

def _split_ids(v: str | List[int] | None) -> List[int]:
    if v is None:
        return []
    if isinstance(v, list):
        return [int(x) for x in v]
    raw = v.replace(";", ",").replace(" ", ",")
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return [int(p) for p in parts]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )

    bot_token: str = Field(alias="BOT_TOKEN")
    admin_ids: List[int] = Field(default_factory=list, alias="ADMIN_IDS")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        return _split_ids(v)

    def get_admin_ids(self) -> List[int]:
        return list(self.admin_ids)

settings = Settings()
