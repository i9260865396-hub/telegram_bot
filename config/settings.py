from typing import List
from pydantic import field_validator
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
    BOT_TOKEN: str
    ADMIN_IDS: List[int] = []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        return _split_ids(v)

settings = Settings()
