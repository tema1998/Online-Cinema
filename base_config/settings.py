import os
from typing import ClassVar
from pydantic import Field
from pydantic_settings import BaseSettings


class BaseProjectSettings(BaseSettings):
    class Config:
        env_file = '.env'

    # Project settings
    base_dir: ClassVar[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_name: str = Field('consumer_app', alias='PROJECT_NAME')

    # RabbitMQ connection settings
    rabbitmq_host: str = Field('127.0.0.1', alias='RABBITMQ_HOST')
    rabbitmq_connection_port: int = Field(5672, alias='RABBITMQ_CONNECTION_PORT')
    rabbitmq_management_port: int = Field(15672, alias='RABBITMQ_MANAGEMENT_PORT')
    rabbitmq_default_user: str = Field('guest', alias='RABBITMQ_DEFAULT_USER')
    rabbitmq_default_pass: str = Field('guest', alias='RABBITMQ_DEFAULT_PASS')

    # RabbitMQ queue and exchange settings
    dlx_exchange: str = Field('dlx_exchange', alias='DLX_EXCHANGE')
    default_exchange: str = Field('default_exchange', alias='DLX_EXCHANGE')

    instant_message_dlq: str = Field('instant_message_dlq', alias='INSTANT_MESSAGE_DLQ')
    instant_message_queue: str = Field('instant_message', alias='INSTANT_MESSAGE_QUEUE')
    scheduled_message_queue: str = Field('scheduled_message', alias='SCHEDULED_MESSAGE_QUEUE')

    instant_notification_dlq: str = Field('instant_notification_dlq', alias='INSTANT_NOTIFICATION_DLQ')
    instant_notification_queue: str = Field('instant_notification', alias='INSTANT_NOTIFICATION_QUEUE')
    scheduled_notification_queue: str = Field('scheduled_notification', alias='SCHEDULED_NOTIFICATION_QUEUE')

    max_retries_dlq: int = Field(5, alias='MAX_RETRIES_DLQ')

    @property
    def rabbitmq_connection_url(self) -> str:
        return f"amqp://{self.rabbitmq_default_user}:{self.rabbitmq_default_pass}@{self.rabbitmq_host}:{self.rabbitmq_connection_port}/"


settings = BaseProjectSettings()
