import random
from http import HTTPStatus
import pytest

from tests.functional.testdata.person_data import person_data

index_name = 'persons'
api_url = '/api/v1/persons'


@pytest.mark.asyncio
class TestPersons:

    async def test_get_all_persons(self, make_get_request):
        response = await make_get_request(f'{api_url}')

        assert response.status == HTTPStatus.OK
        assert len(response.body) == len(person_data)

    async def test_person_by_id(self, make_get_request):
        person = person_data[random.randint(0, len(person_data) - 1)]
        person_id = person['id']

        response = await make_get_request(f'{api_url}/{person_id}')

        assert response.status == HTTPStatus.OK
        assert response.body['uuid'] == person['id']
        assert response.body['full_name'] == person['name']

    async def test_search_person(self, make_get_request):
        person = person_data[random.randint(0, len(person_data) - 1)]
        person_full_name = person['name']

        person_name = person['name'].split(' ')[0]

        response = await make_get_request(f'{api_url}/search', {'query': person_name})

        assert response.status == HTTPStatus.OK
        assert len(response.body) == 1
        assert response.body[0]['uuid'] == person['id']
        assert response.body[0]['full_name'] == person_full_name

    async def test_persons_pagination(self, make_get_request):
        response = await make_get_request(f'{api_url}', {'page_size': 3, 'page': 1})

        assert response.status == HTTPStatus.OK
        assert len(response.body) == 3

    async def test_film_with_person_by_id(self, make_get_request):
        person_id = 'f025498f-a5c3-4418-9bb1-adcb702e91a0'

        response = await make_get_request(f'{api_url}/{person_id}')

        assert response.status == HTTPStatus.OK
        assert len(response.body) == 3

    async def test_film_with_person_by_id_pagination(self, make_get_request):
        person_id = 'b1e6f9d0-0a7e-4bb2-a1de-a632e354f42b'

        response = await make_get_request(f'{api_url}/{person_id}/film', {'page_size': 3, 'page': 2})

        assert response.status == HTTPStatus.OK
        # In the DB 4 films with this genre, page_size=3, on the second page will be 1 film.
        assert len(response.body) == 1

    async def test_persons_cache(self, redis_client, make_get_request):
        person = person_data[random.randint(0, len(person_data) - 1)]
        person_id = person['id']

        response = await make_get_request(f'{api_url}/{person_id}')

        assert response.status == HTTPStatus.OK
        assert response.body['uuid'] == person['id']
        assert response.body['full_name'] == person['name']

        # Get all keys from redis.
        redis_keys = redis_client.keys()
        assert len(redis_keys) == 1

        # Get cached values
        cached_values = redis_client.get(redis_keys[0])

        assert person['id'] in cached_values
