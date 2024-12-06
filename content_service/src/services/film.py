from typing import Optional, List

from fastapi import Depends
from models.film import FilmListInput

from db.async_search_engine import AsyncSearchEngine
from db.elastic_async_search_engine import ElasticAsyncSearchEngine
from db.elastic_async_search_engine import get_search_engine
from services.base_service import BaseService


class FilmService(BaseService):
    """Film Service."""

    index = "movies"

    def __init__(self, search_engine: AsyncSearchEngine):
        super().__init__(search_engine, self.index)

    async def get_films_list_filtered_searched_sorted(
        self,
        query: Optional[str] = None,
        genre_id: Optional[str] = None,
        sort: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 50,
    ) -> List[FilmListInput] | None:
        """Retrieve a list of films with optional sorting, genre filtering, and full-text search."""

        sort_dict = {"+": "asc", "-": "desc"}

        # Construct filter conditions
        filter_conditions = []
        if genre_id:
            filter_conditions.append(
                {
                    "nested": {
                        "path": "genres",
                        "query": {
                            "bool": {"must": [{"term": {"genres.id": genre_id}}]}
                        },
                    }
                }
            )

        # Construct search conditions
        search_conditions = []
        if query:
            search_conditions.append({"match": {"title": query}})

        # Build the query
        query_body = {
            "size": page_size,
            "query": {"bool": {"must": search_conditions, "filter": filter_conditions}},
            "from": (page_number - 1) * page_size,
        }

        # Add sorting if provided
        if sort is not None and sort != "-":
            sort_field = sort[1:] if sort.startswith(
                ("+", "-")) else "imdb_rating"
            sort_order = (
                sort_dict.get(sort[0], "desc")
                if sort.startswith(("+", "-"))
                else "desc"
            )
            query_body["sort"] = [{sort_field: {"order": sort_order}}]

        search_results = await self.search(query_body=query_body)
        if search_results:
            return [FilmListInput(**item) for item in search_results]
        return None

    async def get_similar_films(
        self, film_id: str, page_number: int = 1, page_size: int = 50
    ) -> List[FilmListInput] | None:
        """Retrieve similar films based on genre."""

        # Retrieve the film details from Elasticsearch
        film = await self.get_by_id(film_id)
        if not film:
            return []

        # Extract genres from the retrieved film
        genres = [genre["id"] for genre in film.get("genres", [])]

        # Build the query to find similar films based on the extracted genres
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
                                                "terms": {"genres.id": genres}
                                            }  # Match any of the genres
                                        ]
                                    }
                                },
                            }
                        }
                    ],
                    "must_not": [
                        {"term": {"id": film_id}}  # Exclude the original film
                    ],
                }
            },
            "from": (page_number - 1) * page_size,  # Pagination
        }

        search_results = await self.search(query_body=query_body)
        if search_results:
            return [FilmListInput(**item) for item in search_results]
        return None


# The main dependency function to create the FilmService
def get_film_service(
    search_engine: ElasticAsyncSearchEngine = Depends(get_search_engine),
) -> FilmService:
    return FilmService(search_engine)
