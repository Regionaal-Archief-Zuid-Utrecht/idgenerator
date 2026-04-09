import pytest
from src.validator import ValidationError


class TestIdentifierGeneration:
    def test_generate_first_identifier_for_producer_dataset(self, generator):
        identifier, is_new = generator.generate(
            "g0352", "689", "Informatieobject", "Archief", None, None
        )
        
        assert identifier == "nl-wbdrazu-g0352-689-1"
        assert is_new is True

    def test_generate_sequential_numbering(self, generator):
        id1, _ = generator.generate("g0352", "689", "Informatieobject", "Archief", None, None)
        id2, _ = generator.generate("g0352", "689", "Bestand", "Serie", None, None)
        id3, _ = generator.generate("g0352", "689", "Informatieobject", "Dossier", "INV-001", None)
        
        assert id1 == "nl-wbdrazu-g0352-689-1"
        assert id2 == "nl-wbdrazu-g0352-689-2"
        assert id3 == "nl-wbdrazu-g0352-689-3"

    def test_generate_different_producers_independent(self, generator):
        id1, _ = generator.generate("g0352", "689", "Informatieobject", "Archief", None, None)
        id2, _ = generator.generate("k5090", "689", "Informatieobject", "Archief", None, None)
        
        assert id1 == "nl-wbdrazu-g0352-689-1"
        assert id2 == "nl-wbdrazu-k5090-689-1"

    def test_generate_different_datasets_independent(self, generator):
        id1, _ = generator.generate("g0352", "689", "Informatieobject", "Archief", None, None)
        id2, _ = generator.generate("g0352", "690", "Informatieobject", "Archief", None, None)
        
        assert id1 == "nl-wbdrazu-g0352-689-1"
        assert id2 == "nl-wbdrazu-g0352-690-1"

    def test_generate_duplicate_detection(self, generator):
        id1, is_new1 = generator.generate("g0352", "689", "Informatieobject", "Archief", None, None)
        id2, is_new2 = generator.generate("g0352", "689", "Informatieobject", "Archief", None, None)
        
        assert id1 == id2
        assert is_new1 is True
        assert is_new2 is False

    def test_generate_uniqueness_key_all_params(self, generator):
        id1, _ = generator.generate(
            "g0352", "689", "Informatieobject", "Archiefstuk", "INV-001", "path/a"
        )
        id2, is_new2 = generator.generate(
            "g0352", "689", "Informatieobject", "Archiefstuk", "INV-001", "path/a"
        )
        id3, is_new3 = generator.generate(
            "g0352", "689", "Informatieobject", "Archiefstuk", "INV-002", "path/a"
        )
        
        assert id1 == id2
        assert is_new2 is False
        assert id3 != id1
        assert is_new3 is True

    def test_generate_lowercase_identifier(self, generator):
        identifier, _ = generator.generate(
            "G0352", "689", "Informatieobject", "Archief", None, None
        )
        
        assert identifier == "nl-wbdrazu-g0352-689-1"

    def test_generate_with_trimmed_inventarisnummer(self, generator):
        id1, _ = generator.generate(
            "g0352", "689", "Informatieobject", "Dossier", "  INV-001  ", None
        )
        id2, is_new2 = generator.generate(
            "g0352", "689", "Informatieobject", "Dossier", "INV-001", None
        )
        
        assert id1 == id2
        assert is_new2 is False


class TestIdentifierValidation:
    def test_generate_with_invalid_type_raises_error(self, generator):
        with pytest.raises(ValidationError):
            generator.generate("g0352", "689", "InvalidType", "Archief", None, None)

    def test_generate_archief_with_inventarisnummer_raises_error(self, generator):
        with pytest.raises(ValidationError):
            generator.generate("g0352", "689", "Informatieobject", "Archief", "INV-001", None)

    def test_generate_dossier_without_inventarisnummer_raises_error(self, generator):
        with pytest.raises(ValidationError):
            generator.generate("g0352", "689", "Informatieobject", "Dossier", None, None)

    def test_generate_archiefstuk_without_filepath_raises_error(self, generator):
        with pytest.raises(ValidationError):
            generator.generate("g0352", "689", "Informatieobject", "Archiefstuk", "INV-001", None)
