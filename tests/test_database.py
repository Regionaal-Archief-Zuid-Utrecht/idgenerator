import os
import sqlite3
import tempfile

import pytest
from razu_idgenerator.database import Database
from razu_idgenerator.generator import IdentifierGenerator


@pytest.fixture
def legacy_db():
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE identifiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producer TEXT NOT NULL,
            dataset TEXT NOT NULL,
            type TEXT NOT NULL,
            aggregationlevel TEXT NOT NULL,
            inventarisnummer TEXT,
            filepath TEXT,
            unique_number INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(producer, dataset, type, aggregationlevel, inventarisnummer, filepath)
        )
    """)
    cursor.execute("""
        CREATE INDEX idx_producer_dataset
        ON identifiers(producer, dataset)
    """)
    conn.commit()
    conn.close()

    database = Database(db_path)
    yield database

    if os.path.exists(db_path):
        os.remove(db_path)


class TestDatabaseMigration:
    def test_migrates_aggregationlevel_to_nullable(self, legacy_db):
        conn = sqlite3.connect(legacy_db.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(identifiers)")
        columns = {col[1]: col for col in cursor.fetchall()}
        conn.close()

        assert columns['aggregationlevel'][3] == 0

    def test_can_insert_bestand_with_null_aggregationlevel_after_migration(self, legacy_db):
        generator = IdentifierGenerator(legacy_db)

        identifier, is_new, _ = generator.generate(
            "g0352", "689", "Bestand", "Archiefstuk", "INV-001", "path/file.pdf"
        )

        assert is_new is True
        assert identifier == "nl-wbdrazu-g0352-689-1"
