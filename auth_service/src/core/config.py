from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Project settings"""

    project_name: str = "auth_service"
    secret_key: str

    auth_algorithm: str
    public_key: str
    private_key: str
    yandex_oauth_client_id: str
    yandex_oauth_client_secret: str
    yandex_oauth_authorize_url: str
    yandex_oauth_redirect_uri: str
    yandex_oauth_token_url: str
    yandex_oauth_info_url: str

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

    jaeger_host: str
    jaeger_port: int

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
