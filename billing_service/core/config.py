import os
from logging import config as logging_config
from core.logger import LOGGING
from typing import ClassVar

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    subsctiption_project_name: str = os.getenv("BILLING_PROJECT_NAME", "Subscription")

    # PG settings
    pg_user: str = os.getenv("BILLING_DB_USER", "user_subscription")
    pg_pass: str = os.getenv("BILLING_DB_PASSWORD", "123456")
    pg_host: str = os.getenv("BILLING_DB_HOST", "localhost")
    pg_port: int = os.getenv("BILLING_DB_PORT", 5434)
    pg_db: str = os.getenv("BILLING_DB", "db_subscription")

    sqlalchemy_echo: bool = os.getenv("SQLALCHEMY_ECHO", False)

    # Secret key for JWT
    secret_key: str = os.getenv("SECRET_KEY", "secret")

    auth_service_get_user_info_url: str = os.getenv("AUTH_SERVICE_GET_USER_INFO_URL", "secret")

    # Yookassa
    yookassa_shop_id : str = os.getenv("YOOKASSA_SHOP_ID", "shop_id")
    yookassa_secret_key : str = os.getenv("YOOKASSA_SECRET_KEY", "secret_key")
    yookassa_return_url : str = os.getenv("YOOKASSA_RETURN_URL", "https://yandex-team-number-2.ru")
    @property
    def dsn(self) -> str:
        return f'postgresql+asyncpg://{self.pg_user}:{self.pg_pass}@{self.pg_host}:{self.pg_port}/{self.pg_db}'



# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

config = Settings()