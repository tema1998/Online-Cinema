from pydantic import Field
from base_config.settings import BaseProjectSettings


class Settings(BaseProjectSettings):
    # SMTP settings
    smtp_pass: str = Field('code', alias='SMTP_PASS')
    smtp_email: str = Field('email', alias='SMTP_EMAIL')
    smtp_host: str = Field('smtp.yandex.ru', alias='SMTP_HOST')
    smtp_port: int = Field(465, alias='SMTP_PORT')

    # PostgreSQL settings
    postgres_host: str = Field('127.0.0.1', alias='POSTGRES_HOST')
    postgres_user: str = Field('practix_user', alias='POSTGRES_USER')
    postgres_password: str = Field('practix_password', alias='POSTGRES_PASSWORD')
    postgres_db: str = Field('notification_db', alias='POSTGRES_DB')
    postgres_port: int = Field(5432, alias='POSTRGES_PORT')

    @property
    def postgres_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()
