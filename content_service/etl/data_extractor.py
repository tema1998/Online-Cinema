import logging

import psycopg
from psycopg import ClientCursor
from psycopg.rows import dict_row

from backoff import backoff
from queries import generate_filmwork_query, generate_person_query, generate_genre_query


class DataExtractor:
    def __init__(self, table_name: str, database_params: dict, batch_size: int):
        self.table_name = table_name
        self.database_params = database_params
        self.batch_size = batch_size
        self.last_modified = "1970-01-01 00:00:00"  # Initial value for last modified

    def extract(self):
        data, size_of_current_batch, self.last_modified = self.extract_data_from_db(
            self.last_modified
        )
        return data

    @backoff(limit_of_retries=10)
    def extract_data_from_db(self, last_modified: str) -> (list, int, str):
        """
        Method extracts data from postgres DB.
        :param last_modified: Last modified of data.
        :return: List of data, size of current batch, modified datetime of last entry.
        """
        with psycopg.connect(
            **self.database_params, row_factory=dict_row, cursor_factory=ClientCursor
        ) as conn, conn.cursor() as cursor:

            if self.table_name == "film_work":
                cursor.execute(generate_filmwork_query(
                    last_modified, self.batch_size))

            elif self.table_name == "person":
                cursor.execute(generate_person_query(
                    last_modified, self.batch_size))

            elif self.table_name == "genre":
                cursor.execute(generate_genre_query(
                    last_modified, self.batch_size))

            executed_data = cursor.fetchall()
            size_of_current_batch = len(executed_data)

            # Get modified date of the last entry in the batch.
            if size_of_current_batch == 0:
                logging.info("There is no new data to extract.")
                return [], 0, last_modified

            last_modified = str(executed_data[-1]["modified"])

            return executed_data, size_of_current_batch, last_modified
