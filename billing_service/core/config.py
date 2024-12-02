import os
from logging import config as logging_config
from core.logger import LOGGING
from pydantic import Field

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    billing_project_name: str = os.getenv("BILLING_PROJECT_NAME", "Subscription")

    # PG settings
    pg_user: str = os.getenv("BILLING_DB_USER", "user_subscription")
    pg_pass: str = os.getenv("BILLING_DB_PASSWORD", "123456")
    pg_host: str = os.getenv("BILLING_DB_HOST", "localhost")
    pg_port: int = os.getenv("BILLING_DB_PORT", 5434)
    pg_db: str = os.getenv("BILLING_DB", "db_subscription")

    sqlalchemy_echo: bool = os.getenv("SQLALCHEMY_ECHO", False)

    # Secret key for JWT
    secret_key: str = os.getenv("SECRET_KEY", "secret")

    auth_service_url: str = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8081/")

    auth_service_get_user_info: str = os.getenv(
        "AUTH_SERVICE_GET_USER_INFO_HANDLER", "api/v1/auth/user-info"
    )

    auth_service_set_premium_user: str = os.getenv("AUTH_SERVICE_SET_PREMIUM_HANDLER", "api/v1/premium/set-premium-status")

    # Yookassa
    yookassa_shop_id: str = os.getenv("YOOKASSA_SHOP_ID", "shop_id")
    yookassa_secret_key: str = os.getenv("YOOKASSA_SECRET_KEY", "secret_key")
    yookassa_return_url: str = os.getenv(
        "YOOKASSA_RETURN_URL", "https://yandex-team-number-2.ru"
    )

    # RabbitMQ Billing connection settings
    rabbitmq_host_billing: str = Field('127.0.0.1', alias='RABBITMQ_BILLING_HOST')
    rabbitmq_connection_port_billing: int = Field(5672, alias="RABBITMQ_BILLING_CONNECTION_PORT")
    rabbitmq_management_port_billing: int = Field(15672, alias="RABBITMQ_BILLING_MANAGEMENT_PORT")
    rabbitmq_default_user_billing: str = Field('guest', alias='RABBITMQ_BILLING_DEFAULT_USER')
    rabbitmq_default_pass_billing: str = Field('guest', alias='RABBITMQ_BILLING_DEFAULT_PASS')

    # RabbitMQ Billing queue and exchange settings
    dlx_exchange_billing: str = Field('dlx_exchange_billing', alias='DLX_EXCHANGE_BILLING')
    default_exchange_billing: str = Field('default_exchange_billing', alias='DEFAULT_EXCHANGE_BILLING')

    billing_premium_subscription_success_queue: str = Field('billing_premium_subscription_success_queue', alias='BILLING_PREMIUM_SUBSCRIPTION_SUCCESS_QUEUE')
    billing_premium_subscription_fail_queue: str = Field('billing_premium_subscription_fail_queue', alias='BILLING_PREMIUM_SUBSCRIPTION_FAIL_QUEUE')
    billing_film_purchase_success_queue: str = Field('billing_film_purchase_success_queue', alias='BILLING_FILM_PURCHASE_SUCCESS_QUEUE')
    billing_film_purchase_fail_queue: str = Field('billing_film_purchase_fail_queue', alias='BILLING_FILM_PURCHASE_FAIL_QUEUE')

    billing_premium_subscription_success_dlq: str = Field('billing_premium_subscription_success_dlq', alias='BILLING_PREMIUM_SUBSCRIPTION_SUCCESS_DLQ')
    billing_premium_subscription_fail_dlq: str = Field('billing_premium_subscription_fail_dlq', alias='BILLING_PREMIUM_SUBSCRIPTION_FAIL_DLQ')
    billing_film_purchase_success_dlq: str = Field('billing_film_purchase_success_dlq', alias='BILLING_FILM_PURCHASE_SUCCESS_DLQ')
    billing_film_purchase_fail_dlq: str = Field('billing_film_purchase_fail_dlq', alias='BILLING_FILM_PURCHASE_FAIL_DLQ')

    @property
    def dsn(self) -> str:
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_pass}@{self.pg_host}:{self.pg_port}/{self.pg_db}"

    @property
    def rabbitmq_billing_connection_url(self) -> str:
        return f"amqp://{self.rabbitmq_default_user_billing}:{self.rabbitmq_default_pass_billing}@{self.rabbitmq_host_billing}:{self.rabbitmq_connection_port_billing}/"


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

config = Settings()
