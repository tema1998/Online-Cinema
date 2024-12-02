import os
from typing import ClassVar
from pydantic import Field
from pydantic_settings import BaseSettings


class BaseProjectSettings(BaseSettings):
    class Config:
        env_file = ".env"

    # Project settings
    base_dir: ClassVar[str] = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    project_name: str = Field("consumer_app", alias="PROJECT_NAME")

    # RabbitMQ Notification connection settings
    rabbitmq_host: str = Field("127.0.0.1", alias="RABBITMQ_NOTIFICATION_HOST")
    rabbitmq_connection_port: int = Field(
        5672, alias="RABBITMQ_NOTIFICATION_CONNECTION_PORT"
    )
    rabbitmq_management_port: int = Field(
        15672, alias="RABBITMQ_NOTIFICATION_MANAGEMENT_PORT"
    )
    rabbitmq_default_user: str = Field(
        "guest", alias="RABBITMQ_NOTIFICATION_DEFAULT_USER"
    )
    rabbitmq_default_pass: str = Field(
        "guest", alias="RABBITMQ_NOTIFICATION_DEFAULT_PASS"
    )

    # RabbitMQ Notification queue and exchange settings
    dlx_exchange: str = Field("dlx_exchange", alias="DLX_EXCHANGE")
    default_exchange: str = Field("default_exchange", alias="DLX_EXCHANGE")

    instant_message_dlq: str = Field("instant_message_dlq", alias="INSTANT_MESSAGE_DLQ")
    instant_message_queue: str = Field("instant_message", alias="INSTANT_MESSAGE_QUEUE")
    scheduled_message_queue: str = Field(
        "scheduled_message", alias="SCHEDULED_MESSAGE_QUEUE"
    )

    instant_notification_dlq: str = Field(
        "instant_notification_dlq", alias="INSTANT_NOTIFICATION_DLQ"
    )
    instant_notification_queue: str = Field(
        "instant_notification", alias="INSTANT_NOTIFICATION_QUEUE"
    )
    scheduled_notification_queue: str = Field(
        "scheduled_notification", alias="SCHEDULED_NOTIFICATION_QUEUE"
    )

    max_retries_dlq: int = Field(5, alias="MAX_RETRIES_DLQ")

    # RabbitMQ Billing connection settings
    rabbitmq_host_billing: str = Field('127.0.0.1', alias='RABBITMQ_BILLING_HOST')
    rabbitmq_connection_port_billing: int = Field(5672, alias="RABBITMQ_BILLING_CONNECTION_PORT")
    rabbitmq_management_port_billing: int = Field(15672, alias="RABBITMQ_BILLING_MANAGEMENT_PORT")
    rabbitmq_default_user_billing: str = Field('guest', alias='RABBITMQ_BILLING_DEFAULT_USER')
    rabbitmq_default_pass_billing: str = Field('guest', alias='RABBITMQ_BILLING_DEFAULT_PASS')

    # RabbitMQ Billing queue and exchange settings
    dlx_exchange_billing: str = Field('dlx_exchange_billing', alias='DLX_EXCHANGE_BILLING')
    default_exchange_billing: str = Field('default_exchange_billing', alias='DEFAULT_EXCHANGE_BILLING')

    billing_premium_subscription_success_queue: str = Field('billing_premium_subscription_success_queue',
                                                            alias='BILLING_PREMIUM_SUBSCRIPTION_SUCCESS_QUEUE')
    billing_premium_subscription_fail_queue: str = Field('billing_premium_subscription_fail_queue',
                                                         alias='BILLING_PREMIUM_SUBSCRIPTION_FAIL_QUEUE')
    billing_film_purchase_success_queue: str = Field('billing_film_purchase_success_queue',
                                                     alias='BILLING_FILM_PURCHASE_SUCCESS_QUEUE')
    billing_film_purchase_fail_queue: str = Field('billing_film_purchase_fail_queue',
                                                  alias='BILLING_FILM_PURCHASE_FAIL_QUEUE')

    billing_premium_subscription_success_dlq: str = Field('billing_premium_subscription_success_dlq',
                                                          alias='BILLING_PREMIUM_SUBSCRIPTION_SUCCESS_DLQ')
    billing_premium_subscription_fail_dlq: str = Field('billing_premium_subscription_fail_dlq',
                                                       alias='BILLING_PREMIUM_SUBSCRIPTION_FAIL_DLQ')
    billing_film_purchase_success_dlq: str = Field('billing_film_purchase_success_dlq',
                                                   alias='BILLING_FILM_PURCHASE_SUCCESS_DLQ')
    billing_film_purchase_fail_dlq: str = Field('billing_film_purchase_fail_dlq',
                                                alias='BILLING_FILM_PURCHASE_FAIL_DLQ')

    @property
    def rabbitmq_connection_url(self) -> str:
        return f"amqp://{self.rabbitmq_default_user}:{self.rabbitmq_default_pass}@{self.rabbitmq_host}:{self.rabbitmq_connection_port}/"

    @property
    def rabbitmq_billing_connection_url(self) -> str:
        return f"amqp://{self.rabbitmq_default_user_billing}:{self.rabbitmq_default_pass_billing}@{self.rabbitmq_host_billing}:{self.rabbitmq_connection_port_billing}/"


settings = BaseProjectSettings()
