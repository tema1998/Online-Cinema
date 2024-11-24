from abc import ABC, abstractmethod
from typing import Any, List, Optional


class AsyncRepository(ABC):
    @abstractmethod
    async def fetch_by_id(self, index: str, record_id: str) -> Optional[Any]:
        """Fetch a record by its ID from the specified index (e.g., table, collection)."""
        pass

    @abstractmethod
    async def fetch_by_query(self, index: str, query: Any) -> Optional[List[Any]]:
        """Fetch records based on a query from the specified index (e.g., table, collection)."""
        pass

    @abstractmethod
    async def fetch_all(self, index: str) -> Optional[List[Any]]:
        """Fetch all records from the specified index (e.g., table, collection)."""
        pass

    @abstractmethod
    async def insert(self, index: str, record: Any) -> Any:
        """Insert a new record into the specified index (e.g., table, collection)."""
        pass

    @abstractmethod
    async def update(self, index: str, record_id: str, record: Any) -> Any:
        """Update an existing record by its ID in the specified index (e.g., table, collection)."""
        pass

    @abstractmethod
    async def delete(self, index: str, record_id: str) -> Any:
        """Delete a record by its ID from the specified index (e.g., table, collection)."""
        pass
