import os
from logging import config as logging_config

from pydantic import BaseSettings, Field

from core.logger import LOGGING


class Settings(BaseSettings):
    # Корень проекта
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Название проекта. Используется в Swagger-документации
    project_name: str = Field(
        env="FASTAPI_AUTH_PROJECT_NAME", default="movies")

    elastic_host: str = Field(env="ES_HOST", default="127.0.0.1")
    elastic_port: int = Field(env="ES_PORT", default=9200)
    elastic_schema = os.getenv("ES_SCHEMA", "http://")

    redis_host: str = Field(env="REDIS_HOST", default="127.0.0.1")
    redis_port: int = Field(env="REDIS_PORT", default=6379)

    secret_key: str = os.getenv("SECRET_KEY", "practix")

    limit_of_requests_per_minute: int = os.getenv(
        "LIMIT_OF_REQUESTS_PER_MINUTE", 20)

    billing_service_url: str = os.getenv(
        "BILLING_SERVICE_URL", "http://billing_service:8082/")
    billing_service_check_whether_user_bought_film: str = os.getenv("BILLING_SERVICE_CHECK_WHETHER_USER_BOUGHT_FILM",
                                                                    "api/v1/order/check-user-film")

    def es_url(self):
        return f"{self.elastic_schema}{self.elastic_host}:{self.elastic_port}"


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

config = Settings()
