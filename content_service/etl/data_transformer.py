from backoff import backoff
from models import Film, PersonData, GenreData


class DataTransformer:
    @backoff(limit_of_retries=10)
    def transform(self, index_name, data_from_db):
        """
        Function for transforming data from DB to format for ElasticSearch.
        :param index_name: The name of index.
        :param data_from_db: Data from DB.
        :return: Transformed data for loading to the ElasticSearch.
        """
        transformed_data = []
        try:
            if index_name == "movies":
                transformed_data = [{"_index": index_name,
                                     "_id": str(entry["id"]),
                                     "_source": Film(
                                         id=str(entry["id"]),
                                         title=entry["title"],
                                         description=entry["description"],
                                         imdb_rating=entry["rating"],
                                         genres=entry["genres"],
                                         actors=entry["actors"],
                                         directors=entry["directors"],
                                         writers=entry["writers"]
                                     ).dict()
                                     }
                                    for entry in data_from_db]
            elif index_name == "genres":
                transformed_data = [{"_index": index_name,
                                     "_id": str(entry["id"]),
                                     "_source": GenreData(
                                         id=str(entry["id"]),
                                         name=entry["name"],
                                         description=entry["description"],
                                     ).dict()
                                     }
                                    for entry in data_from_db]
            elif index_name == "persons":
                transformed_data = [{"_index": index_name,
                                     "_id": str(entry["id"]),
                                     "_source": PersonData(
                                         id=str(entry["id"]),
                                         name=entry["name"],
                                     ).dict()
                                     }
                                    for entry in data_from_db]
        except KeyError as e:
            print(f"Key error: {e} - ensure the database fields match the model fields.")
        except Exception as e:
            print(f"An unexpected error occurred during data transformation: {e}")

        return transformed_data
