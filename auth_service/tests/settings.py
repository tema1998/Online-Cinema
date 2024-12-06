from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project name used in Swagger documentation
    project_name: str = Field(
        default="movies", json_schema_extra={"env": "AUTH_PROJECT_NAME"}
    )

    api_schema: ClassVar[str] = "http://"
    api_host: str = Field(default="127.0.0.1",
                          json_schema_extra={"env": "API_HOST"})
    api_port: int = Field(default=8080, json_schema_extra={"env": "API_PORT"})

    redis_host: str = Field(
        default="127.0.0.1", json_schema_extra={"env": "REDIS_HOST"}
    )
    redis_port: int = Field(default=6379, json_schema_extra={
                            "env": "REDIS_PORT"})

    # PostgreSQL connection settings
    pg_user: str = Field(default="db_user", json_schema_extra={
                         "env": "POSTGRES_USER"})
    pg_pass: str = Field(
        default="123qwe", json_schema_extra={"env": "POSTGRES_PASSWORD"}
    )
    pg_host: str = Field(
        default="db_auth_test", json_schema_extra={"env": "POSTGRES_HOST"}
    )
    pg_port: int = Field(default=5432, json_schema_extra={
                         "env": "POSTGRES_PORT"})
    pg_db: str = Field(default="db_auth", json_schema_extra={
                       "env": "POSTGRES_DB"})
    pg_engine: str = Field(
        default="django.db.backends.postgresql",
        json_schema_extra={"env": "POSTGRES_ENGINE"},
    )
    sqlalchemy_echo: bool = Field(
        default=False, json_schema_extra={"env": "SQLALCHEMY_ECHO"}
    )

    secret_key: str = Field(default="practix", json_schema_extra={
                            "env": "SECRET_KEY"})

    @property
    def api_url(self) -> str:
        return f"{self.api_schema}{self.api_host}:{self.api_port}"

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_pass}@{self.pg_host}:{self.pg_port}/{self.pg_db}"


# Initialize settings
test_settings = Settings()
