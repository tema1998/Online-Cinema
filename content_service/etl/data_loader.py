import logging

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from backoff import backoff

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DataLoader:
    def __init__(self, elasticsearch_host: str, index_name: str):
        self.elasticsearch_host = elasticsearch_host
        self.index_name = index_name

    @backoff(limit_of_retries=10)
    def load(self, data: list):
        """
        Function for loading data to Elasticsearch.
        :param data: List with prepared data for inserting to Elasticsearch.
        :return: Result of loading to ES.
        """
        client = Elasticsearch(hosts=self.elasticsearch_host)
        success, _ = bulk(
            client, data
        )  # `success` is the number of successfully indexed documents
        logging.info(
            f"Successfully indexed {success} records into index {self.index_name}"
        )
        return success
