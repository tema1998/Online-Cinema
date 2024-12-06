from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core.config import config

# Create an asynchronous engine using the configuration DSN
engine = create_async_engine(
    config.dsn, echo=config.sqlalchemy_echo, future=True)

# Create an asynchronous session factory
async_session_factory = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Dependency to provide a session to FastAPI routes or other parts of the application
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
