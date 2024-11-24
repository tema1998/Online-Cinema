from datetime import timedelta

from pydantic import Field
from base_config.settings import BaseProjectSettings


class Settings(BaseProjectSettings):
    # Middleware settings
    middleware_secret_key: str = Field('practix', alias='MIDDLEWARE_SECRET_KEY')

    # JWT settings
    secret_key: str = Field('practix', alias='SECRET_KEY')

    # Short link settings
    redirect_url: str = Field('http://localhost:8000/', alias='REDIRECT_URL')
    expires_in: timedelta = Field(timedelta(hours=48), alias='EXPIRES_IN')
    confirmation_base_url: str = Field('http://localhost:8000/confirm-email', alias='CONFIRMATION_BASE_URL')

    # Redis
    redis_host: str = "redis"
    redis_port: int = "6379"

    get_user_info_url: str = Field('http://auth_service:8081/api/v1/auth/get-user-info', alias='GET_USER_INFO_URL')

    @property
    def rabbitmq_connection_url(self) -> str:
        return f'amqp://{self.rabbitmq_default_user}:{self.rabbitmq_default_pass}@{self.rabbitmq_host}:{self.rabbitmq_connection_port}/'


settings = Settings()
