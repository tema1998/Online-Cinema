import asyncio
import aiohttp
import pytest_asyncio
import redis
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings
from tests.functional.testdata.models import Response

pytest_plugins = [
    "tests.functional.fixtures.es_utils",
    "tests.functional.fixtures.es_data",
]


@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client():
    """
    Fixture for getting ES client.
    :return:
    """
    es_client = AsyncElasticsearch(hosts=test_settings.es_url(), verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture
def make_get_request():
    async def inner(query: str, params: dict = None) -> Response:
        """
        Fixture for making request to API.
        :param query: Query url.
        :param params: Parameters of query.
        :return:
        """
        url = f"{test_settings.api_url()}{query}"

        session = aiohttp.ClientSession()

        async with session.get(url, params=params) as response:
            return Response(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest_asyncio.fixture(scope="function")
async def redis_client():
    """
    Fixture clear redis storage before return it.
    And clear redis storage when close connection.
    """
    client = redis.Redis(
        test_settings.redis_host, test_settings.redis_port,
        decode_responses=True
    )

    client.flushdb(asynchronous=True)
    yield client
    client.flushdb(asynchronous=True)
