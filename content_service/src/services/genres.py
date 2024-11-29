from operator import index
from typing import Optional, List

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import FilmListInput
from models.genre import Genre

from db.async_search_engine import AsyncSearchEngine
from db.elastic import get_elastic
from db.elastic_async_search_engine import ElasticAsyncSearchEngine
from db.elastic_async_search_engine import get_search_engine
from services.base_service import BaseService


class GenreService(BaseService):
    """Сервис жанров."""

    index = "genres"

    def __init__(self, search_engine: AsyncSearchEngine):
        super().__init__(search_engine, self.index)

    async def genre_list(self, page_number: int, page_size: int) -> list[Genre] | None:
        """Получение списка жанров."""

        query_body = {
            "size": page_size,
            "query": {"match_all": {}},
            "from": (page_number - 1) * page_size,
        }

        search_results = await self.search(query_body=query_body)

        if search_results:
            return [Genre(**item) for item in search_results]
        return None

    async def get_popular_films(
        self, genre_id: str, page_number: int = 1, page_size: int = 50
    ) -> Optional[List[FilmListInput]]:
        """Retrieve films sorted by IMDb rating based on genre ID."""

        # Build the query to filter by nested genre and sort by IMDb rating
        query_body = {
            "size": page_size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "nested": {
                                "path": "genres",
                                "query": {
                                    "bool": {
                                        "must": [
                                            {
                                                "term": {"genres.id": genre_id}
                                            }  # Filter by genre ID
                                        ]
                                    }
                                },
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "imdb_rating": {"order": "desc"}
                }  # Sort by IMDb rating in descending order
            ],
            "from": (page_number - 1) * page_size,  # Pagination
        }

        search_results = await self.search(query_body=query_body, index="movies")

        if search_results:
            return [FilmListInput(**item) for item in search_results]
        return None


# The main dependency function to create the GenreService
def get_genre_service(
    search_engine: ElasticAsyncSearchEngine = Depends(get_search_engine),
) -> GenreService:
    return GenreService(search_engine)
