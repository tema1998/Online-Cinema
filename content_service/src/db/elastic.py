from typing import Optional

from core.config import config
from elasticsearch import AsyncElasticsearch

es: Optional[AsyncElasticsearch] = None


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch:
    return AsyncElasticsearch(hosts=[f"{config.es_url()}"])


# Dependency function to create the Elasticsearch client
def get_elastic_client() -> AsyncElasticsearch:
    return AsyncElasticsearch(hosts=[f"{config.es_url()}"])
