from typing import Any, List, Optional

from db.async_search_engine import AsyncSearchEngine
from db.elastic import get_elastic_client
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends


class ElasticAsyncSearchEngine(AsyncSearchEngine):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, index: str, _id: str) -> Any | None:
        try:
            doc = await self.elastic.get(index=index, id=_id)
            return doc["_source"]
        except NotFoundError:
            return None

    async def search_by_query(
        self, index: str, query_body: dict
    ) -> Optional[List[Any]]:
        try:
            response = await self.elastic.search(index=index, body=query_body)
            hits = response["hits"]["hits"]
            if not hits:
                return []
            return [hit["_source"] for hit in hits]
        except NotFoundError:
            return None


# Dependency function to create the ElasticAsyncSearchEngine
def get_search_engine(
    elastic_client: AsyncElasticsearch = Depends(get_elastic_client),
) -> ElasticAsyncSearchEngine:
    return ElasticAsyncSearchEngine(elastic_client)
