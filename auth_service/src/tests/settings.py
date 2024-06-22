from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class RedisSettings(BaseSettings):
    """Конфигурация для Redis"""

    redis_host: str = "127.0.0.1"
    redis_port: int = 6379


class PostgresSettings(BaseSettings):
    """Конфигурация для Postgres"""

    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_user: str
    postgres_db: str
    postgres_password: str

    db_dsn: str


class TestSettings(BaseSettings):
    """Конфигурация проекта для тестирования"""

    auth_api_url: str = "http://127.0.0.1:8000"

    auth_algorithm: str = "RS256"
    public_key: str
    private_key: str

    redis: RedisSettings = RedisSettings()
    postgres: PostgresSettings = PostgresSettings()


test_settings = TestSettings()
