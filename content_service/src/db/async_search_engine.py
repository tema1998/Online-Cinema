from abc import ABC, abstractmethod
from typing import Any, List, Optional


class AsyncSearchEngine(ABC):
    @abstractmethod
    async def get_by_id(self, index: str, _id: str) -> Any | None:
        pass

    @abstractmethod
    async def search_by_query(self, index: str, query_body: dict) -> Optional[List[Any]]:
        pass
