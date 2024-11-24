from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from consumer_notification_recorder.config.settings import settings

# Create the base for declarative models
Base = declarative_base()

# Create an async engine
engine = create_async_engine(settings.postgres_url, echo=True)

# Create a sessionmaker
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Dependency for getting an async session
async def get_db_session() -> AsyncSession:
    return async_session()


# Initialize the database
async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
