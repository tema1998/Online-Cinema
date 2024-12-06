import logging

from elasticsearch import Elasticsearch

from backoff import backoff


class IndexManager:
    def __init__(self, elasticsearch_host: str, index_name: str, index: dict):
        self.elasticsearch_host = elasticsearch_host
        self.index_name = index_name
        self.index = index

    @backoff(limit_of_retries=10)
    def create_index_if_doesnt_exist(self) -> None:
        client = Elasticsearch(hosts=self.elasticsearch_host)
        if not client.indices.exists(index=self.index_name):
            response = client.indices.create(
                index=self.index_name, **self.index)
            if response.get("acknowledged"):
                logging.info(
                    f"Index {self.index_name} was created successfully.")
            else:
                logging.error("Error of creating index.")
