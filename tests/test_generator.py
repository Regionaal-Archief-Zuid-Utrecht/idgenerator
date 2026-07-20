import concurrent.futures

import pytest
from razu_idgenerator.generator import IdentifierGenerator
from razu_idgenerator.validator import ValidationError


class TestIdentifierGeneration:
    def test_generate_first_identifier_for_producer_dataset(self, generator):
        identifier, is_new, stepped_dir = generator.generate(
            "g0352", "689", "Informatieobject", "Archief", None, None
        )
        
        assert identifier == "nl-wbdrazu-g0352-689-1"
        assert is_new is True
        assert stepped_dir == "000/000/"

    def test_generate_sequential_numbering(self, generator):
        id1, _, stepped_dir1 = generator.generate("g0352", "689", "Informatieobject", "Archief", None, None)
        id2, _, stepped_dir2 = generator.generate("g0352", "689", "Bestand", "Serie", None, "path/file.pdf")
        id3, _, stepped_dir3 = generator.generate("g0352", "689", "Informatieobject", "Dossier", "INV-001", None)
        
        assert id1 == "nl-wbdrazu-g0352-689-1"
        assert id2 == "nl-wbdrazu-g0352-689-2"
        assert id3 == "nl-wbdrazu-g0352-689-3"
        assert stepped_dir1 == "000/000/"
        assert stepped_dir2 == "000/000/"
        assert stepped_dir3 == "000/000/"

    def test_generate_different_producers_independent(self, generator):
        id1, _, _ = generator.generate("g0352", "689", "Informatieobject", "Archief", None, None)
        id2, _, _ = generator.generate("k5090", "689", "Informatieobject", "Archief", None, None)
        
        assert id1 == "nl-wbdrazu-g0352-689-1"
        assert id2 == "nl-wbdrazu-k5090-689-1"

    def test_generate_different_datasets_independent(self, generator):
        id1, _, _ = generator.generate("g0352", "689", "Informatieobject", "Archief", None, None)
        id2, _, _ = generator.generate("g0352", "690", "Informatieobject", "Archief", None, None)
        
        assert id1 == "nl-wbdrazu-g0352-689-1"
        assert id2 == "nl-wbdrazu-g0352-690-1"

    def test_generate_duplicate_detection(self, generator):
        id1, is_new1, stepped_dir1 = generator.generate("g0352", "689", "Informatieobject", "Archief", None, None)
        id2, is_new2, stepped_dir2 = generator.generate("g0352", "689", "Informatieobject", "Archief", None, None)
        
        assert id1 == id2
        assert is_new1 is True
        assert is_new2 is False
        assert stepped_dir1 == stepped_dir2

    def test_generate_uniqueness_key_all_params(self, generator):
        id1, _, _ = generator.generate(
            "g0352", "689", "Informatieobject", "Archiefstuk", "INV-001", "path/a"
        )
        id2, is_new2, _ = generator.generate(
            "g0352", "689", "Informatieobject", "Archiefstuk", "INV-001", "path/a"
        )
        id3, is_new3, _ = generator.generate(
            "g0352", "689", "Informatieobject", "Archiefstuk", "INV-002", "path/a"
        )
        
        assert id1 == id2
        assert is_new2 is False
        assert id3 != id1
        assert is_new3 is True

    def test_generate_lowercase_identifier(self, generator):
        identifier, _, _ = generator.generate(
            "G0352", "689", "Informatieobject", "Archief", None, None
        )
        
        assert identifier == "nl-wbdrazu-g0352-689-1"

    def test_generate_case_insensitive_producer_and_dataset(self, generator):
        id1, is_new1, _ = generator.generate(
            "G0352", "689", "Informatieobject", "Archief", None, None
        )
        id2, is_new2, _ = generator.generate(
            "g0352", "689", "Informatieobject", "Archief", None, None
        )

        assert id1 == id2 == "nl-wbdrazu-g0352-689-1"
        assert is_new1 is True
        assert is_new2 is False

    def test_generate_strips_whitespace_from_producer_and_dataset(self, generator):
        identifier1, is_new1, _ = generator.generate(
            "  G0352  ", "  689  ", "Informatieobject", "Archief", None, None
        )
        identifier2, is_new2, _ = generator.generate(
            "G0352", "689", "Informatieobject", "Archief", None, None
        )

        assert identifier1 == "nl-wbdrazu-g0352-689-1"
        assert identifier1 == identifier2
        assert is_new1 is True
        assert is_new2 is False

    def test_generate_bestand_ignores_aggregationlevel_and_inventarisnummer(self, generator):
        id1, is_new1, _ = generator.generate(
            "g0352", "689", "Bestand", "Archiefstuk", "INV-001", "path/a"
        )
        id2, is_new2, _ = generator.generate(
            "g0352", "689", "Bestand", None, None, "path/a"
        )

        assert id1 == id2
        assert is_new1 is True
        assert is_new2 is False

    def test_generate_with_trimmed_inventarisnummer(self, generator):
        id1, _, _ = generator.generate(
            "g0352", "689", "Informatieobject", "Dossier", "  INV-001  ", None
        )
        id2, is_new2, _ = generator.generate(
            "g0352", "689", "Informatieobject", "Dossier", "INV-001", None
        )
        
        assert id1 == id2
        assert is_new2 is False

    def test_concurrent_generations_produce_unique_numbers(self, db):
        gen = IdentifierGenerator(db)

        def generate(i):
            return gen.generate(
                "g0352", "689", "Informatieobject", "Dossier", f"INV-{i:04d}", None
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(generate, range(100)))

        identifiers = [result[0] for result in results]
        unique_identifiers = set(identifiers)

        assert len(unique_identifiers) == 100, (
            f"Expected 100 unique identifiers, got {len(unique_identifiers)}"
        )

        numbers = sorted(
            int(identifier.split("-")[-1]) for identifier in unique_identifiers
        )
        assert numbers == list(range(1, 101)), (
            f"Expected sequential numbers 1-100, got {numbers}"
        )

    def test_concurrent_duplicate_requests_return_same_identifier(self, db):
        gen = IdentifierGenerator(db)

        def generate(_):
            return gen.generate(
                "g0352", "689", "Informatieobject", "Archief", None, None
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(generate, range(20)))

        identifiers = [result[0] for result in results]
        is_new_values = [result[1] for result in results]

        assert len(set(identifiers)) == 1, (
            f"Expected a single identifier, got {set(identifiers)}"
        )
        assert sum(is_new_values) == 1, (
            f"Expected exactly one new identifier, got {sum(is_new_values)}"
        )

    @pytest.mark.parametrize(
        "unique_number, expected",
        [
            (1, "000/000/"),
            (999, "000/000/"),
            (1000, "000/001/"),
            (815224, "000/815/"),
            (999999, "000/999/"),
            (1000000, "001/000/"),
            (1001000, "001/001/"),
        ]
    )
    def test_make_stepped_dir_from_id(self, unique_number, expected):
        assert IdentifierGenerator.make_stepped_dir_from_id(unique_number) == expected


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
