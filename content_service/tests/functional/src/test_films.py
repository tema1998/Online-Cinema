import math
import random
from http import HTTPStatus
import pytest

from tests.functional.testdata.film_data import film_data
from tests.functional.testdata.models import FilmSummary

index_name = 'films'
api_url = '/api/v1/films'


@pytest.mark.asyncio
class TestFilmsAPI:

    @classmethod
    def sort_nested_dict(cls, d):
        if isinstance(d, dict):
            return {k: cls.sort_nested_dict(v) for k, v in sorted(d.items())}
        elif isinstance(d, list):
            if all(isinstance(i, dict) for i in d):
                return [cls.sort_nested_dict(i) for i in d]
            else:
                return [cls.sort_nested_dict(i) for i in sorted(d)]
        else:
            return d

    @classmethod
    def replace_key(cls, data, old_key, new_key):
        if isinstance(data, dict):
            return {
                new_key if key == old_key else key: cls.replace_key(value, old_key, new_key)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [cls.replace_key(item, old_key, new_key) for item in data]
        else:
            return data

    async def test_retrieve_film_list(self, make_get_request):
        response = await make_get_request(f'{api_url}')
        assert response.status == HTTPStatus.OK
        assert len(response.body) == len(film_data)

    async def test_film_by_id(self, make_get_request):
        film = random.choice(film_data)
        film_id, film_title = film['id'], film['title']
        updated_film = TestFilmsAPI.replace_key(film, 'id', 'uuid')
        response = await make_get_request(f'{api_url}/{film_id}')
        response_body_updated = TestFilmsAPI.replace_key(response.body, 'full_name', 'name')
        updated_film_sorted = TestFilmsAPI.sort_nested_dict(updated_film)
        response_body_updated_sorted = TestFilmsAPI.sort_nested_dict(response_body_updated)

        assert response.status == HTTPStatus.OK
        assert updated_film_sorted == response_body_updated_sorted

    async def test_search_films(self, make_get_request):
        film = random.choice(film_data)
        film_title = film['title']

        response = await make_get_request(f'{api_url}/search', {'query': film_title})

        assert response.status == HTTPStatus.OK
        assert response.body[0]['uuid'] == film['id']
        assert response.body[0]['title'] == film_title

    async def test_sort_films(self, make_get_request):
        transformed_data = []
        for film in film_data:
            summary = FilmSummary(uuid=film['id'], title=film['title'], imdb_rating=film['imdb_rating'])
            transformed_data.append(summary.dict())

        sorted_film_data_desc = sorted(transformed_data, key=lambda x: x['imdb_rating'], reverse=True)
        sorted_film_data_asc = sorted(transformed_data, key=lambda x: x['imdb_rating'], reverse=False)

        response_desc = await make_get_request(f'{api_url}', {'sort': '-imdb_rating'})
        response_asc = await make_get_request(f'{api_url}', {'sort': '+imdb_rating'})

        assert response_desc.status == HTTPStatus.OK
        assert len(response_desc.body) == len(film_data)
        assert response_desc.body == sorted_film_data_desc
        assert response_asc.status == HTTPStatus.OK
        assert len(response_asc.body) == len(film_data)
        assert response_asc.body == sorted_film_data_asc

    async def test_sort_films_and_filter(self, make_get_request):
        film = random.choice(film_data)
        genre_id = film['genres'][0]['id']
        filtered_films = [
            film for film in film_data
            if any(genre['id'] == genre_id for genre in film['genres'])
        ]
        transformed_data = []
        for film in filtered_films:
            summary = FilmSummary(uuid=film['id'], title=film['title'], imdb_rating=film['imdb_rating'])
            transformed_data.append(summary.dict())

        sorted_film_data_desc = sorted(transformed_data, key=lambda x: x['imdb_rating'], reverse=True)
        sorted_film_data_asc = sorted(transformed_data, key=lambda x: x['imdb_rating'], reverse=False)

        response_desc = await make_get_request(f'{api_url}', {'sort': '-imdb_rating', 'genre': genre_id})
        response_asc = await make_get_request(f'{api_url}', {'sort': '+imdb_rating', 'genre': genre_id})

        assert response_desc.status == HTTPStatus.OK
        assert len(response_desc.body) == len(filtered_films)
        assert response_desc.body == sorted_film_data_desc
        assert response_asc.status == HTTPStatus.OK
        assert len(response_asc.body) == len(filtered_films)
        assert response_asc.body == sorted_film_data_asc

    async def test_films_pagination(self, make_get_request):
        PAGE_SIZE = 3
        objects_number = len(film_data)
        pages_number = math.ceil(objects_number / PAGE_SIZE)
        last_pages_objects_number = objects_number % PAGE_SIZE
        response = await make_get_request(f'{api_url}', {'page_size': PAGE_SIZE, 'page': pages_number})

        assert response.status == HTTPStatus.OK
        assert len(response.body) == last_pages_objects_number

    async def test_films_cache(self, redis_client, make_get_request):
        film = random.choice(film_data)
        film_id = film['id']

        response = await make_get_request(f'{api_url}/{film_id}')

        assert response.status == HTTPStatus.OK
        assert response.body['uuid'] == film['id']
        assert response.body['title'] == film['title']

        redis_keys = redis_client.keys()
        assert len(redis_keys) == 1

        cached_values = redis_client.get(redis_keys[0])

        assert film['id'] in cached_values
