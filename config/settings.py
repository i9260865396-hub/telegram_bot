# config/settings.py
from pydantic_settings import BaseSettings
from typing import List, Set


def _split_ids(v) -> list[int]:
    """Превращает ADMIN_IDS из строки или числа в список int."""
    if isinstance(v, int):
        v = str(v)
    elif not isinstance(v, str):
        return []
    raw = v.replace(";", ",").replace(" ", ",")
    return [int(x) for x in raw.split(",") if x.strip()]


class Settings(BaseSettings):
    bot_token: str
    admin_ids: str | int | None = ""   # допускаем строку, число или пусто
    database_url: str = "sqlite+aiosqlite:///./bot.db"
    log_level: str = "INFO"

    def get_admin_ids(self) -> Set[int]:
        """Возвращает admin_ids как set[int]."""
        return set(_split_ids(self.admin_ids))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
