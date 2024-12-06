import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

import aiohttp
import pytest_asyncio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

from src.db.db_utils import Base
from src.services.async_pg_repository import PostgresAsyncRepository
from src.services.user_service import UserService
from tests.settings import test_settings
from tests.test_data.schemes import Response

pytest_plugins = [
    "tests.fixtures.pg_data",
    # "tests.functional.fixtures.es_data",
]

# Create the async session factory
async_session_factory = sessionmaker(
    class_=AsyncSession, expire_on_commit=False)


# Dependency to provide a session to FastAPI routes or other parts of the application
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


async def create_database(engine: AsyncEngine) -> None:
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def purge_database(engine: AsyncEngine) -> None:
    """Drop all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Custom event loop policy (if needed)
class CustomEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    def new_event_loop(self):
        loop = super().new_event_loop()
        # Add any custom configuration here
        return loop


# Create a session-scoped event loop
@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# Apply the custom event loop policy
@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop_policy():
    policy = CustomEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    yield
    # Cleanup (if needed)
    asyncio.set_event_loop_policy(None)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_engine(event_loop):
    """Create an asynchronous SQLAlchemy engine for the test database using test settings."""
    loop = asyncio.get_running_loop()
    engine = create_async_engine(
        test_settings.db_url, echo=test_settings.sqlalchemy_echo, future=True
    )
    await create_database(engine)
    yield engine
    await purge_database(engine)
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_session(db_engine):
    """Create a new asynchronous database session for a test."""
    async_session_factory.configure(bind=db_engine)
    async with async_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def redis_client():
    """Create a Redis client for testing using test settings."""
    client = Redis(host=test_settings.redis_host,
                   port=test_settings.redis_port)

    yield client
    await client.flushdb()
    await client.aclose()


@pytest_asyncio.fixture(scope="session")
async def postgres_repo() -> PostgresAsyncRepository:
    # Use a test database connection string
    test_dsn = "postgresql+asyncpg://test_user:test_password@localhost/test_db"
    return PostgresAsyncRepository(test_dsn)


@pytest_asyncio.fixture(scope="session")
async def user_service(
    postgres_repo: PostgresAsyncRepository, redis_client: Redis
) -> UserService:
    # Create the UserService instance with the PostgresAsyncRepository and Redis client
    return UserService(
        db=postgres_repo, redis=redis_client, secret_key=test_settings.secret_key
    )


@pytest_asyncio.fixture
def make_get_request(scope="session"):
    async def inner(
        query: str, params: dict = None, headers: dict[str, Any] | None = None
    ) -> Response:
        """
        Fixture for making GET request to API.
        :param query: Query url.
        :param params: Parameters of query.
        :return:
        """
        url = f"{test_settings.api_url}{query}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                return Response(
                    body=await response.json(),
                    headers=response.headers,
                    status=response.status,
                )

    return inner


@pytest_asyncio.fixture(scope="session")
def make_post_request():
    async def inner(
        query: str,
        form_data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Response:
        """
        Fixture for making POST request to API.
        @param headers: Headers.
        @param query: Query string.
        @param form_data: Body.
        @return: Response model.
        """

        url = f"{test_settings.api_url}{query}"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=url, json=form_data, headers=headers
            ) as response:
                return Response(
                    body=await response.json(),
                    headers=response.headers,
                    status=response.status,
                )

    return inner


@pytest_asyncio.fixture(scope="session")
def make_delete_request():
    async def inner(
        query: str,
        form_data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Response:
        """
        Fixture for making DELETE request to API.
        @param headers: Headers.
        @param query: Query string.
        @param form_data: Body.
        @return: Response model.
        """

        url = f"{test_settings.api_url}{query}"

        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=url, json=form_data, headers=headers
            ) as response:
                return Response(
                    body=await response.json(),
                    headers=response.headers,
                    status=response.status,
                )

    return inner


@pytest_asyncio.fixture(scope="session")
def make_update_request():
    async def inner(
        query: str,
        form_data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Response:
        """
        Fixture for making PUT request to API.
        @param headers: Headers.
        @param query: Query string.
        @param form_data: Body.
        @return: Response model.
        """

        url = f"{test_settings.api_url}{query}"

        async with aiohttp.ClientSession() as session:
            async with session.put(
                url=url, json=form_data, headers=headers
            ) as response:
                return Response(
                    body=await response.json(),
                    headers=response.headers,
                    status=response.status,
                )

    return inner
