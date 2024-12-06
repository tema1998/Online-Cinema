from typing import List

import pytest_asyncio
from elasticsearch.helpers import async_bulk


@pytest_asyncio.fixture(name="es_remove_if_exists_and_create_index", scope="session")
def es_remove_if_exists_and_create_index(es_client):
    async def inner(index_name: str, index_settings: dict):
        """
        Fixture removes index with all data if it exists.
        Then create index without data.
        :param index_name:  The name of index.
        :param index_settings: Dictionary settings for creating index.
        """
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)
        await es_client.indices.create(index=index_name, **index_settings)

    return inner


@pytest_asyncio.fixture(name="es_remove_index", scope="session")
def es_remove_index(es_client):
    async def inner(index_name: str):
        """
        Fixture removes index with all data.
        :param index_name:  The name of index.
        """
        await es_client.indices.delete(index=index_name)

    return inner


@pytest_asyncio.fixture(name="es_write_data", scope="session")
def es_write_data(es_client):
    async def inner(index_name: str, data: List[dict], refresh: str = None):
        """
        Fixture adds prepared data to index.
        :param index_name: The name of index.
        :param data: Prepared data for writing to index.
        :param refresh: Refresh policy for making the data immediately searchable.
        """
        updated, errors = await async_bulk(
            client=es_client, actions=data, refresh=refresh
        )

        if errors:
            raise Exception(
                f"Error of data adding to {index_name} index of ES.")

    return inner
