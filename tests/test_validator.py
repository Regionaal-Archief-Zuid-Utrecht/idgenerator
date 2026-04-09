import pytest
from src.validator import Validator, ValidationError


class TestValidatorRequiredParams:
    def test_validate_missing_producer_raises_error(self):
        with pytest.raises(ValidationError, match="producer"):
            Validator.validate_request(None, "689", "Informatieobject", "Archief", None, None)

    def test_validate_missing_dataset_raises_error(self):
        with pytest.raises(ValidationError, match="dataset"):
            Validator.validate_request("g0352", None, "Informatieobject", "Archief", None, None)

    def test_validate_missing_type_raises_error(self):
        with pytest.raises(ValidationError, match="type"):
            Validator.validate_request("g0352", "689", None, "Archief", None, None)

    def test_validate_missing_aggregationlevel_raises_error(self):
        with pytest.raises(ValidationError, match="aggregationlevel"):
            Validator.validate_request("g0352", "689", "Informatieobject", None, None, None)

    def test_validate_empty_producer_raises_error(self):
        with pytest.raises(ValidationError, match="producer"):
            Validator.validate_request("", "689", "Informatieobject", "Archief", None, None)

    def test_validate_whitespace_producer_raises_error(self):
        with pytest.raises(ValidationError, match="producer"):
            Validator.validate_request("   ", "689", "Informatieobject", "Archief", None, None)


class TestValidatorEnumValues:
    def test_validate_invalid_type_raises_error(self):
        with pytest.raises(ValidationError, match="Invalid type"):
            Validator.validate_request("g0352", "689", "InvalidType", "Archief", None, None)

    def test_validate_lowercase_type_raises_error(self):
        with pytest.raises(ValidationError, match="Invalid type"):
            Validator.validate_request("g0352", "689", "informatieobject", "Archief", None, None)

    def test_validate_invalid_aggregationlevel_raises_error(self):
        with pytest.raises(ValidationError, match="Invalid aggregationlevel"):
            Validator.validate_request("g0352", "689", "Informatieobject", "InvalidLevel", None, None)

    def test_validate_valid_informatieobject_succeeds(self):
        Validator.validate_request("g0352", "689", "Informatieobject", "Archief", None, None)

    def test_validate_valid_bestand_succeeds(self):
        Validator.validate_request("g0352", "689", "Bestand", "Serie", None, None)


class TestValidatorAggregationLevelRules:
    def test_archief_with_inventarisnummer_raises_error(self):
        with pytest.raises(ValidationError, match="must not be provided"):
            Validator.validate_request("g0352", "689", "Informatieobject", "Archief", "INV-001", None)

    def test_archief_with_filepath_raises_error(self):
        with pytest.raises(ValidationError, match="must not be provided"):
            Validator.validate_request("g0352", "689", "Informatieobject", "Archief", None, "path/file.pdf")

    def test_archief_without_optional_params_succeeds(self):
        Validator.validate_request("g0352", "689", "Informatieobject", "Archief", None, None)

    def test_serie_with_inventarisnummer_raises_error(self):
        with pytest.raises(ValidationError, match="must not be provided"):
            Validator.validate_request("g0352", "689", "Informatieobject", "Serie", "INV-001", None)

    def test_serie_without_optional_params_succeeds(self):
        Validator.validate_request("g0352", "689", "Informatieobject", "Serie", None, None)

    def test_dossier_without_inventarisnummer_raises_error(self):
        with pytest.raises(ValidationError, match="required"):
            Validator.validate_request("g0352", "689", "Informatieobject", "Dossier", None, None)

    def test_dossier_with_filepath_raises_error(self):
        with pytest.raises(ValidationError, match="must not be provided"):
            Validator.validate_request("g0352", "689", "Informatieobject", "Dossier", "INV-001", "path/file.pdf")

    def test_dossier_with_inventarisnummer_succeeds(self):
        Validator.validate_request("g0352", "689", "Informatieobject", "Dossier", "INV-001", None)

    def test_archiefstuk_without_inventarisnummer_raises_error(self):
        with pytest.raises(ValidationError, match="required"):
            Validator.validate_request("g0352", "689", "Informatieobject", "Archiefstuk", None, "path/file.pdf")

    def test_archiefstuk_without_filepath_raises_error(self):
        with pytest.raises(ValidationError, match="required"):
            Validator.validate_request("g0352", "689", "Informatieobject", "Archiefstuk", "INV-001", None)

    def test_archiefstuk_with_both_params_succeeds(self):
        Validator.validate_request("g0352", "689", "Informatieobject", "Archiefstuk", "INV-001", "path/file.pdf")


class TestValidatorNormalization:
    def test_normalize_inventarisnummer_trims_whitespace(self):
        result = Validator.normalize_inventarisnummer("  INV-001  ")
        assert result == "INV-001"

    def test_normalize_inventarisnummer_whitespace_only_returns_none(self):
        result = Validator.normalize_inventarisnummer("   ")
        assert result is None

    def test_normalize_inventarisnummer_none_returns_none(self):
        result = Validator.normalize_inventarisnummer(None)
        assert result is None

    def test_normalize_filepath_trims_whitespace(self):
        result = Validator.normalize_filepath("  path/file.pdf  ")
        assert result == "path/file.pdf"
