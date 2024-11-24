from typing import Type, TypeVar, Generic, List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

T = TypeVar("T")


class BaseService(Generic[T]):
    def __init__(self, model: Type[T], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def create(self, **kwargs: Dict[str, Any]) -> T:
        """Create a new record with the provided fields as keyword arguments."""
        new_instance = self.model(**kwargs)  # Instantiate model with keyword arguments
        try:
            self.db_session.add(new_instance)
            await self.db_session.commit()
            await self.db_session.refresh(new_instance)
            return new_instance
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise Exception(f"Failed to create record: {str(e)}")

    async def get(self, id: UUID) -> Optional[T]:
        """Retrieve a record by ID."""
        query = select(self.model).where(self.model.id == id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[T]:
        """Retrieve all records."""
        query = select(self.model)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def update(self, id: UUID, update_data: Dict[str, Any]) -> Optional[T]:
        """Update a record by ID with provided data."""
        try:
            await self.db_session.execute(
                update(self.model)
                .where(self.model.id == id)
                .values(**update_data)
            )
            await self.db_session.commit()
            return await self.get(id)
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise Exception(f"Failed to update record: {str(e)}")

    async def delete(self, id: UUID) -> bool:
        """Delete a record by ID."""
        try:
            await self.db_session.execute(delete(self.model).where(self.model.id == id))
            await self.db_session.commit()
            return True
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise Exception(f"Failed to delete record: {str(e)}")
