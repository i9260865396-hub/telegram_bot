from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(alias="BOT_TOKEN")
    admin_ids_raw: str = Field(default="", alias="ADMIN_IDS")
    database_url: str = Field(default="sqlite+aiosqlite:///./bot.db", alias="DATABASE_URL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # игнорируем лишние поля в .env
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._admin_ids: list[int] = []
        if self.admin_ids_raw:
            for part in self.admin_ids_raw.replace(";", ",").split(","):
                part = part.strip().strip('"').strip("'")
                if not part:
                    continue
                try:
                    self._admin_ids.append(int(part))
                except ValueError:
                    pass

    @property
    def admin_ids(self) -> list[int]:
        return self._admin_ids


settings = Settings()
