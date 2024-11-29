import time

from data_extractor import DataExtractor
from data_loader import DataLoader
from data_transformer import DataTransformer
from etl import ETL
from index_manager import IndexManager
from indices import movie_index, genre_index, person_index
from settings import BaseConfigs


def run_etl_indefinitely():
    # Initialize configs and settings
    configs = BaseConfigs()

    # Instantiate the components for movies
    index_manager_movies = IndexManager(configs.es_url, "movies", movie_index)
    extractor_movies = DataExtractor("film_work", configs.dsn, configs.batch)
    transformer_movies = DataTransformer()
    loader_movies = DataLoader(configs.es_url, "movies")
    etl_movies = ETL(
        index_manager_movies,
        extractor_movies,
        transformer_movies,
        loader_movies,
        configs.etl_state,
        configs.batch,
        "movies",
    )

    # Instantiate the components for genres
    index_manager_genres = IndexManager(configs.es_url, "genres", genre_index)
    extractor_genres = DataExtractor("genre", configs.dsn, configs.batch)
    transformer_genres = DataTransformer()
    loader_genres = DataLoader(configs.es_url, "genres")
    etl_genres = ETL(
        index_manager_genres,
        extractor_genres,
        transformer_genres,
        loader_genres,
        configs.etl_state,
        configs.batch,
        "genres",
    )

    # Instantiate the components for persons
    index_manager_persons = IndexManager(configs.es_url, "persons", person_index)
    extractor_persons = DataExtractor("person", configs.dsn, configs.batch)
    transformer_persons = DataTransformer()
    loader_persons = DataLoader(configs.es_url, "persons")
    etl_persons = ETL(
        index_manager_persons,
        extractor_persons,
        transformer_persons,
        loader_persons,
        configs.etl_state,
        configs.batch,
        "persons",
    )

    # Run the ETL processes indefinitely
    while True:
        print("Running ETL...")
        # try:
        etl_movies.run_etl()
        etl_genres.run_etl()
        etl_persons.run_etl()
        # except Exception as e:
        #     print(f"An error occurred: {e}")
        print("ETL completed.")
        time.sleep(configs.run_etl_every_seconds)


if __name__ == "__main__":
    run_etl_indefinitely()
