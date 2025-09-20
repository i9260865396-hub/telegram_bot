from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    bot_token: str
    admin_ids: str  # строка из .env, например: "12345,67890"
    database_url: str = "sqlite+aiosqlite:///./bot.db"
    log_level: str = "INFO"

    def get_admin_ids(self) -> List[int]:
        """
        Возвращает список admin_ids как int[] из строки.
        """
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
