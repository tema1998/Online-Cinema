import time
import logging

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError

from tests.functional.settings import Settings
from tests.functional.utils.backoff import backoff

settings = Settings()

logger = logging.getLogger("log")


def es_backoff_logging(details):
    logger.info("Elasticsearch server is not available.")


@backoff(limit_of_retries=0)
def wait_for_es():
    es_client = Elasticsearch(hosts=settings.es_url())
    ping = es_client.ping()
    if ping:
        return ping
    raise TransportError


if __name__ == '__main__':
    wait_for_es()
