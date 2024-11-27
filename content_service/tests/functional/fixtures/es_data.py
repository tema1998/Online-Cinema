import asyncio

import pytest_asyncio

from tests.functional.utils.es_utils import create_bulk_query
from tests.functional.testdata.indices import genre_index, person_index, movie_index
from tests.functional.testdata.genre_data import genre_data
from tests.functional.testdata.film_data import film_data
from tests.functional.testdata.person_data import person_data

indices = [{'index_name': 'movies', 'index_settings': movie_index, 'data': film_data},
           {'index_name': 'persons', 'index_settings': person_index, 'data': person_data},
           {'index_name': 'genres', 'index_settings': genre_index, 'data': genre_data}]


@pytest_asyncio.fixture(name='create_indices', scope="session")
async def create_indices(es_remove_if_exists_and_create_index, es_remove_index):
    """
    Fixture create indices before tests and delete after tests.
    :param es_remove_if_exists_and_create_index: Fixture for creating index.
    :param es_remove_index: Fixture for removing index.
    :return:
    """
    for index in indices:
        await es_remove_if_exists_and_create_index(index_name=index['index_name'],
                                                   index_settings=index['index_settings'])
    yield None
    for index in indices:
        await es_remove_index(index_name=index['index_name'])


@pytest_asyncio.fixture(name='tests_setup', scope="session", autouse=True)
async def tests_setup(create_indices, es_write_data):
    """
    Fixture loads data from all indices to Elasticsearch.
    :return:
    """
    for index in indices:
        bulk_query = create_bulk_query(index_name=index['index_name'], data=index['data'])
        await es_write_data(index_name=index['index_name'], data=bulk_query, refresh="wait_for")

    yield None
