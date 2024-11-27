from data_extractor import DataExtractor
from data_loader import DataLoader
from data_transformer import DataTransformer
from index_manager import IndexManager


class ETL:
    def __init__(
            self,
            index_manager: IndexManager,
            extractor: DataExtractor,
            transformer: DataTransformer,
            loader: DataLoader,
            etl_state: dict,
            batch_size: int,
            index_name: str
    ):
        self.index_manager = index_manager
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader
        self.etl_state = etl_state
        self.batch_size = batch_size
        self.index_name = index_name

    def run_etl(self):
        self.index_manager.create_index_if_doesnt_exist()
        size_of_current_batch = self.batch_size

        while size_of_current_batch == self.batch_size:
            data = self.extractor.extract()
            transformed_data = self.transformer.transform(self.index_name, data)
            self.loader.load(transformed_data)
            size_of_current_batch = len(data)
