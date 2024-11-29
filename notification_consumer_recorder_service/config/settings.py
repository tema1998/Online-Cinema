from pydantic import Field
from base_config.settings import BaseProjectSettings


class Settings(BaseProjectSettings):
    # SMTP settings
    smtp_pass: str = Field('code', alias='SMTP_PASS')
    smtp_email: str = Field('email', alias='SMTP_EMAIL')
    smtp_host: str = Field('smtp.yandex.ru', alias='SMTP_HOST')
    smtp_port: int = Field(465, alias='SMTP_PORT')

    # PostgreSQL settings
    postgres_host: str = Field('127.0.0.1', alias='NOTIFICATION_DB_HOST')
    postgres_user: str = Field('practix_user', alias='NOTIFICATION_DB_USER')
    postgres_password: str = Field('practix_password', alias='NOTIFICATION_DB_PASSWORD')
    postgres_db: str = Field('notification_db', alias='NOTIFICATION_DB')
    postgres_port: int = Field(5432, alias='NOTIFICATION_DB_PORT')

    @property
    def postgres_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()
