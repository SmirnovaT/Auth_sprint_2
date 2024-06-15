from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Project settings"""

    project_name: str = "auth_service"

    auth_algorithm: str
    public_key: str
    private_key: str

    db_dsn: str
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    redis_host: str
    redis_port: int
    redis_user: str
    redis_password: str
    cache_expire_in_seconds: int = 864000

    default_user_role: str

    page_size: int = 10
    page_number: int = 1

    echo: bool = True

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env", extra="ignore"
    )


@lru_cache
def get_settings():
    load_dotenv()
    return Settings()


settings = get_settings()
