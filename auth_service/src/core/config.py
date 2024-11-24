import os
from logging import config as logging_config
from typing import ClassVar

from pydantic_settings import BaseSettings

from src.core.logger import LOGGING


class Settings(BaseSettings):
    # Корень проекта
    base_dir: ClassVar[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Название проекта. Используется в Swagger-документации
    project_name: str = os.getenv("PROJECT_NAME", "movies")

    # Настройки подключения к Redis
    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = os.getenv("REDIS_PORT", 6379)

    # Настройки подключения к PostgreSQL
    pg_user: str = os.getenv("AUTH_POSTGRES_USER", "user_auth")
    pg_pass: str = os.getenv("AUTH_POSTGRES_PASSWORD", "123456")
    pg_host: str = os.getenv("AUTH_POSTGRES_HOST", "localhost")
    pg_port: int = os.getenv("AUTH_POSTGRES_PORT", 5433)
    pg_db: str = os.getenv("AUTH_POSTGRES_DB", "db_auth")
    pg_engine: str = os.getenv("POSTGRES_ENGINE", "django.db.backends.postgresql")

    sqlalchemy_echo: bool = os.getenv("SQLALCHEMY_ECHO", False)

    # Google OAuth settings
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID",
                                      "953340218392-lrsn9fhias75cjffgoesadva2ejfhk9p.apps.googleusercontent.com")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "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")
    google_metadata_url: str = "https://accounts.google.com/.well-known/openid-configuration"

    # Secret key for JWT
    secret_key: str = os.getenv("SECRET_KEY", "practix")

    limit_of_requests_per_minute: int = os.getenv("LIMIT_OF_REQUESTS_PER_MINUTE", 20)

    # Jaeger Config
    enable_tracer: bool = os.getenv("ENABLE_TRACER", False)
    jaeger_host: str = os.getenv("JAEGER_HOST", 'jaeger')
    jaeger_port: int = os.getenv("JAEGER_PORT", 6831)

    # Middleware settings
    middleware_secret_key: str = os.getenv("MIDDLEWARE_SECRET", "super-secret-key")

    @property
    def dsn(self) -> str:
        return f'postgresql+asyncpg://{self.pg_user}:{self.pg_pass}@{self.pg_host}:{self.pg_port}/{self.pg_db}'

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

config = Settings()
