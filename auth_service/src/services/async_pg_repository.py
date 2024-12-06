from typing import Any, List, Optional, Type
from uuid import UUID

# from sqlalchemy.future import select, func
from sqlalchemy import select, func
from sqlalchemy import update, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker

from src.db.db_utils import Base


class PostgresAsyncRepository:
    def __init__(self, dsn: str):
        self.engine = create_async_engine(dsn, echo=True)
        self.async_session = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def fetch_by_id(
        self, model_class: Type[Base], record_id: str
    ) -> Optional[Any]:
        async with self.async_session() as session:
            result = await session.get(model_class, record_id)
            return result

    async def fetch_by_query_all(
        self, model_class: Type[Base], column: str, value: Any
    ) -> Optional[List[Any]]:
        async with self.async_session() as session:
            stmt = select(model_class).where(
                getattr(model_class, column) == value)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def fetch_by_query_all_pagination(
        self,
        model_class: Type[Base],
        column: str,
        value: Any,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Any]:
        async with self.async_session() as session:
            stmt = (
                select(model_class)
                .where(getattr(model_class, column) == value)
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    async def fetch_by_query_all_joinedload(
        self, model_class: Type[Base], column: str, value: Any, joinedload_field: str
    ) -> Optional[List[Any]]:
        """
        Get
        @param model_class: Model
        @param column: Column for condition.
        @param value: Value for condition.
        @param joinedload_field: Joined field to query.
        @return:
        """
        async with self.async_session() as session:
            stmt = (
                select(model_class)
                .options(joinedload(getattr(model_class, joinedload_field)))
                .where(getattr(model_class, column) == value)
            )
            result = await session.execute(stmt)
            return result.scalars().unique().all()

    async def fetch_by_query_first(
        self, model_class: Type[Base], column: str, value: Any
    ) -> Optional[Any]:
        async with self.async_session() as session:
            stmt = select(model_class).where(
                getattr(model_class, column) == value)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def count_by_query(
        self, model_class: Type[Base], column: str, value: Any
    ) -> int:
        async with self.async_session() as session:
            stmt = select(func.count()).where(
                getattr(model_class, column) == value)
            result = await session.execute(stmt)
            return result.scalar()

    async def fetch_by_query_first_many_conditions(
        self, model_class: Type[Base], columns_values: [(str, Any)]
    ) -> Optional[Any]:
        """
        Get first entry by many conditions.
        @param model_class: Model
        @param columns_values: Conditions for query. List of tuples with column's name and values.
        """
        async with self.async_session() as session:
            stmt = select(model_class)
            for column, value in columns_values:
                stmt = stmt.where(getattr(model_class, column) == value)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def fetch_all(self, model_class: Type[Base]) -> Optional[List[Any]]:
        async with self.async_session() as session:
            stmt = select(model_class)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def insert(self, obj: Base) -> Any:
        async with self.async_session() as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def update(self, obj: Base) -> Any:
        async with self.async_session() as session:
            # Convert the SQLAlchemy ORM object to a dictionary of its fields
            obj_dict = {c.name: getattr(obj, c.name)
                        for c in obj.__table__.columns}

            stmt = (
                update(obj.__class__)
                .where(obj.__class__.id == obj.id)
                .values(**obj_dict)
                .execution_options(synchronize_session="fetch")
                .returning(obj.__class__)
            )
            result = await session.execute(stmt)
            await session.commit()

            # Fetch the updated record
            updated_record = result.scalar()
            if updated_record is None:
                raise NoResultFound(
                    f"No {obj.__class__.__name__} found with id: {obj.id}"
                )

            return updated_record

    async def delete(self, model_class: Type[Base], record_id: UUID) -> Any:
        async with self.async_session() as session:
            stmt = (
                delete(model_class)
                .where(model_class.id == record_id)
                .returning(model_class)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar()
