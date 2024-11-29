import random
from http import HTTPStatus
import pytest

from tests.functional.testdata.genre_data import genre_data

index_name = "genres"
api_url = "/api/v1/genres"


@pytest.mark.asyncio
class TestPersons:

    async def test_get_all_persons(self, make_get_request):
        response = await make_get_request(f"{api_url}")

        assert response.status == HTTPStatus.OK
        assert len(response.body) == len(genre_data)

    async def test_genre_by_id(self, make_get_request):
        genre = genre_data[random.randint(0, len(genre_data) - 1)]
        genre_id = genre["id"]

        response = await make_get_request(f"{api_url}/{genre_id}")

        assert response.status == HTTPStatus.OK
        assert response.body["uuid"] == genre["id"]
        assert response.body["name"] == genre["name"]

    async def test_genres_pagination(self, make_get_request):
        response = await make_get_request(f"{api_url}", {"page_size": 3, "page": 1})

        assert response.status == HTTPStatus.OK
        assert len(response.body) == 3

    async def test_genre_popular_films_by_id(self, make_get_request):
        genre_id = "23rf423g-asdq-f544-f433-fwegf53hg533"

        response = await make_get_request(f"{api_url}/{genre_id}/popular")

        films_id = [film["uuid"] for film in response.body]

        assert response.status == HTTPStatus.OK
        assert len(response.body) == 1
        assert films_id[0] == "c0f9dcf1-4110-407c-8fb9-acae55c72629"

    async def test_genre_popular_films_by_id_pagination(self, make_get_request):
        genre_id = "21dszwq3-232d-d21d-9d3s-32dsacr3gv35"

        response = await make_get_request(
            f"{api_url}/{genre_id}/popular", {"page_size": 2, "page": 2}
        )

        assert response.status == HTTPStatus.OK
        # In the DB 3 films with this genre, page_size=2, on the second page will be 1 film.
        assert len(response.body) == 1

    async def test_persons_cache(self, redis_client, make_get_request):
        genre = genre_data[random.randint(0, len(genre_data) - 1)]
        genre_id = genre["id"]

        response = await make_get_request(f"{api_url}/{genre_id}")

        assert response.status == HTTPStatus.OK

        assert response.body["uuid"] == genre["id"]
        assert response.body["name"] == genre["name"]

        # Get all keys from redis.
        redis_keys = redis_client.keys()
        assert len(redis_keys) == 1

        # Get cached values
        cached_values = redis_client.get(redis_keys[0])

        assert genre["id"] in cached_values
