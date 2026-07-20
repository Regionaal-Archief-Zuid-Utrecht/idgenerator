from typing import Optional, Tuple
from .database import Database
from .validator import Validator, ValidationError


class IdentifierGenerator:
    def __init__(self, db: Database):
        self.db = db

    def generate(
        self,
        producer: str,
        dataset: str,
        type: str,
        aggregationlevel: Optional[str] = None,
        inventarisnummer: Optional[str] = None,
        filepath: Optional[str] = None
    ) -> Tuple[str, bool, str]:
        Validator.validate_request(
            producer, dataset, type, aggregationlevel, inventarisnummer, filepath
        )

        producer = Validator.normalize_producer(producer)
        dataset = Validator.normalize_dataset(dataset)
        inventarisnummer = Validator.normalize_inventarisnummer(inventarisnummer)
        filepath = Validator.normalize_filepath(filepath)

        if type == "Bestand":
            aggregationlevel = None
            inventarisnummer = None

        with self.db.transaction() as conn:
            existing_number = self.db._find_identifier(
                conn, producer, dataset, type, aggregationlevel, inventarisnummer, filepath
            )

            if existing_number is not None:
                identifier = self._build_identifier(producer, dataset, existing_number)
                stepped_dir = self.make_stepped_dir_from_id(existing_number)
                return identifier, False, stepped_dir

            unique_number = self.db._get_next_unique_number(conn, producer, dataset)

            self.db._store_identifier(
                conn, producer, dataset, type, aggregationlevel,
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
