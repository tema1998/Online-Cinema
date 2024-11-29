import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tests.settings import Settings
from tests.utils.backoff import backoff

settings = Settings()

logger = logging.getLogger("log")

# Create an asynchronous engine
engine = create_async_engine(settings.db_url, echo=True, future=True)

# Create a configured "Session" class
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


@backoff(limit_of_retries=0)
async def wait_for_postgres():
    try:
        # Use a session to attempt a database connection
        async with AsyncSessionLocal() as session:
            # Attempt a simple query to check the connection
            await session.execute(text("SELECT 1"))
        return True
    except OperationalError as e:
        # Log the error and raise it to trigger a retry
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(wait_for_postgres())
