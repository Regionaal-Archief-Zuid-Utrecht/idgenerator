from typing import Optional, Tuple
from src.database import Database
from src.validator import Validator, ValidationError


class IdentifierGenerator:
    def __init__(self, db: Database):
        self.db = db

    def generate(
        self,
        producer: str,
        dataset: str,
        type: str,
        aggregationlevel: str,
        inventarisnummer: Optional[str] = None,
        filepath: Optional[str] = None
    ) -> Tuple[str, bool, str]:
        Validator.validate_request(
            producer, dataset, type, aggregationlevel, inventarisnummer, filepath
        )

        inventarisnummer = Validator.normalize_inventarisnummer(inventarisnummer)
        filepath = Validator.normalize_filepath(filepath)

        existing_number = self.db.find_identifier(
            producer, dataset, type, aggregationlevel, inventarisnummer, filepath
        )

        if existing_number is not None:
            identifier = self._build_identifier(producer, dataset, existing_number)
            stepped_dir = self.make_stepped_dir_from_id(existing_number)
            return identifier, False, stepped_dir

        unique_number = self.db.get_next_unique_number(producer, dataset)

        self.db.store_identifier(
            producer, dataset, type, aggregationlevel, 
            inventarisnummer, filepath, unique_number
        )

        identifier = self._build_identifier(producer, dataset, unique_number)
        stepped_dir = self.make_stepped_dir_from_id(unique_number)
        return identifier, True, stepped_dir

    @staticmethod
    def _build_identifier(producer: str, dataset: str, unique_number: int) -> str:
        producer_lower = producer.lower()
        dataset_lower = dataset.lower()
        return f"nl-wbdrazu-{producer_lower}-{dataset_lower}-{unique_number}"

    @staticmethod
    def make_stepped_dir_from_id(id: int) -> str:
        millions = id // 1000000
        thousands = id % 1000000 // 1000
        return f"{str(millions).zfill(3)}/{str(thousands).zfill(3)}/"
