import abc
from typing import Optional, Any, List

from db.async_search_engine import AsyncSearchEngine


class BaseService(abc.ABC):
    def __init__(self, search_engine: AsyncSearchEngine, index: str):
        self.search_engine = search_engine
        self.index = index

    async def get_by_id(self, obj_id: str) -> Optional[Any]:
        obj = await self.search_engine.get_by_id(self.index, obj_id)
        return obj

    async def search(
        self, query_body: dict, index: Optional[str] = None
    ) -> Optional[List[Any]]:
        index_to_use = index or self.index
        results = await self.search_engine.search_by_query(
            index_to_use, query_body=query_body
        )
        return results
