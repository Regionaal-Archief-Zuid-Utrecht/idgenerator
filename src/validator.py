from typing import Optional


class ValidationError(Exception):
    pass


class Validator:
    VALID_TYPES = ["Informatieobject", "Bestand"]
    VALID_AGGREGATION_LEVELS = ["Archief", "Serie", "Dossier", "Archiefstuk"]

    @staticmethod
    def validate_request(
        producer: Optional[str],
        dataset: Optional[str],
        type: Optional[str],
        aggregationlevel: Optional[str],
        inventarisnummer: Optional[str],
        filepath: Optional[str]
    ):
        Validator._validate_required_params(producer, dataset, type, aggregationlevel)
        Validator._validate_enum_values(type, aggregationlevel)
        if aggregationlevel is not None:
            Validator._validate_aggregation_level_rules(
                aggregationlevel, inventarisnummer, filepath
            )

    @staticmethod
    def _validate_required_params(
        producer: Optional[str],
        dataset: Optional[str],
        type: Optional[str],
        aggregationlevel: Optional[str]
    ):
        if not producer or not producer.strip():
            raise ValidationError("Missing or empty required parameter: producer")
        if not dataset or not dataset.strip():
            raise ValidationError("Missing or empty required parameter: dataset")
        if not type or not type.strip():
            raise ValidationError("Missing or empty required parameter: type")
        if type != "Bestand" and (not aggregationlevel or not aggregationlevel.strip()):
            raise ValidationError("Missing or empty required parameter: aggregationlevel")

    @staticmethod
    def _validate_enum_values(type: str, aggregationlevel: str):
        if type not in Validator.VALID_TYPES:
            raise ValidationError(
                f"Invalid type: {type}. Must be one of {Validator.VALID_TYPES}"
            )
        if aggregationlevel is not None and aggregationlevel not in Validator.VALID_AGGREGATION_LEVELS:
            raise ValidationError(
                f"Invalid aggregationlevel: {aggregationlevel}. "
                f"Must be one of {Validator.VALID_AGGREGATION_LEVELS}"
            )

    @staticmethod
    def _validate_aggregation_level_rules(
        aggregationlevel: str,
        inventarisnummer: Optional[str],
        filepath: Optional[str]
    ):
        inv_present = inventarisnummer and inventarisnummer.strip()
        fp_present = filepath and filepath.strip()

        if aggregationlevel in ["Archief", "Serie"]:
            if inv_present:
                raise ValidationError(
                    f"inventarisnummer must not be provided for aggregationlevel {aggregationlevel}"
                )
            if fp_present:
                raise ValidationError(
                    f"filepath must not be provided for aggregationlevel {aggregationlevel}"
                )

        elif aggregationlevel == "Dossier":
            if not inv_present:
                raise ValidationError(
                    "inventarisnummer is required for aggregationlevel Dossier"
                )
            if fp_present:
                raise ValidationError(
                    "filepath must not be provided for aggregationlevel Dossier"
                )

        elif aggregationlevel == "Archiefstuk":
            if not inv_present:
                raise ValidationError(
                    "inventarisnummer is required for aggregationlevel Archiefstuk"
                )
            if not fp_present:
                raise ValidationError(
                    "filepath is required for aggregationlevel Archiefstuk"
                )

    @staticmethod
    def normalize_inventarisnummer(inventarisnummer: Optional[str]) -> Optional[str]:
        if inventarisnummer is None:
            return None
        trimmed = inventarisnummer.strip()
        return trimmed if trimmed else None

    @staticmethod
    def normalize_filepath(filepath: Optional[str]) -> Optional[str]:
        if filepath is None:
            return None
        trimmed = filepath.strip()
        return trimmed if trimmed else None
