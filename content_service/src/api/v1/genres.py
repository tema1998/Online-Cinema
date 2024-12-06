from typing import List, Annotated

from core.pagination import PaginationParams
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi_cache.decorator import cache
from models.film import FilmListOutput
from models.genre import Genre
from services.bearer import security_jwt
from services.genres import GenreService, get_genre_service
from starlette import status

router = APIRouter()


@router.get(
    "/",
    response_model=list[Genre],
    response_model_by_alias=False,
    summary="Список жанров",
)
@cache(expire=60)
async def genres(
    genre_service: GenreService = Depends(get_genre_service),
    pagination: PaginationParams = Depends(PaginationParams),
) -> list[Genre]:
    genres_list = await genre_service.genre_list(pagination.page, pagination.page_size)
    if not genres_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no genres."
        )

    return genres_list


@router.get(
    "/{genre_id}",
    response_model=Genre,
    response_model_by_alias=False,
    summary="Деталка жанра",
)
@cache(expire=60)
async def genres(
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no such genre."
        )

    return genre


@router.get(
    "/{genre_id}/popular",
    response_model=List[FilmListOutput],
    summary="Get popular films by genre",
)
@cache(expire=60)
async def genres(
    genre_id: str = Path(
        ..., description="The ID of the genre for which to find films"
    ),
    pagination: PaginationParams = Depends(PaginationParams),
    genre_service: GenreService = Depends(get_genre_service),
) -> List[FilmListOutput]:
    films = await genre_service.get_popular_films(
        genre_id=genre_id, page_number=pagination.page, page_size=pagination.page_size
    )

    if not films:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no films of such genre.",
        )

    return [
        FilmListOutput(uuid=film.uuid, title=film.title,
                       imdb_rating=film.imdb_rating)
        for film in films
    ]
