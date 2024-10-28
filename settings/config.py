from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Конфігураційний файл для настроювання."""

    token: str = Field(alias="BOT_TOKEN")
    USERS_FILE_NAME: str = Field(alias="USERS_FILE", default="users.json")
    PROXIES_FILE_NAME: str = Field(alias="PROXIES_FILE", default="proxies.json")

    class Config:
        env_file = ".env"
