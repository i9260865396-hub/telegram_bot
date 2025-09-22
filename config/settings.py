from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

def _split_ids(v: str | List[int] | None) -> List[int]:
    if v is None:
        return []
    if isinstance(v, int):
        return [v]
    if isinstance(v, list):
        return [int(x) for x in v]
    raw = v.replace(";", ",").replace(" ", ",")
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return [int(p) for p in parts]

_ROOT_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_DB_PATH = (_ROOT_DIR / "database" / "bot.db").resolve()


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: List[int] = []
    DATABASE_URL: str = Field(
        default=f"sqlite+aiosqlite:///{_DEFAULT_DB_PATH.as_posix()}"
    )
    LOG_LEVEL: str = "INFO"

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

    @property
    def bot_token(self) -> str:
        return self.BOT_TOKEN

    @property
    def admin_ids(self) -> List[int]:
        return self.ADMIN_IDS

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def log_level(self) -> str:
        return self.LOG_LEVEL

settings = Settings()
