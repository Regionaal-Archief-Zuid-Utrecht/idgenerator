import sqlite3
from contextlib import contextmanager
from typing import Optional


class Database:
    VALID_MODES = {"DEFERRED", "IMMEDIATE", "EXCLUSIVE"}

    def __init__(self, db_path: str = "identifiers.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS identifiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producer TEXT NOT NULL,
                dataset TEXT NOT NULL,
                type TEXT NOT NULL,
                aggregationlevel TEXT,
                inventarisnummer TEXT,
                filepath TEXT,
                unique_number INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(producer, dataset, type, aggregationlevel, inventarisnummer, filepath)
            )
        """)

        cursor.execute("PRAGMA table_info(identifiers)")
        columns = cursor.fetchall()
        aggregationlevel_info = next(
            (col for col in columns if col[1] == 'aggregationlevel'), None
        )
        if aggregationlevel_info and aggregationlevel_info[3]:
            self._make_aggregationlevel_nullable(conn)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_producer_dataset
            ON identifiers(producer, dataset)
        """)

        conn.commit()
        conn.close()

    def _make_aggregationlevel_nullable(self, conn: sqlite3.Connection):
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE identifiers_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producer TEXT NOT NULL,
                dataset TEXT NOT NULL,
                type TEXT NOT NULL,
                aggregationlevel TEXT,
                inventarisnummer TEXT,
                filepath TEXT,
                unique_number INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(producer, dataset, type, aggregationlevel, inventarisnummer, filepath)
            )
        """)
        cursor.execute("""
            INSERT INTO identifiers_new
            (id, producer, dataset, type, aggregationlevel, inventarisnummer, filepath, unique_number, created_at)
            SELECT id, producer, dataset, type, aggregationlevel, inventarisnummer, filepath, unique_number, created_at
            FROM identifiers
        """)
        cursor.execute("DROP TABLE identifiers")
        cursor.execute("ALTER TABLE identifiers_new RENAME TO identifiers")
        cursor.execute("""
            INSERT OR REPLACE INTO sqlite_sequence (name, seq)
            VALUES ('identifiers', (SELECT MAX(id) FROM identifiers))
        """)

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def transaction(self, mode: str = "IMMEDIATE"):
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid transaction mode: {mode}")

        conn = sqlite3.connect(self.db_path, isolation_level=None)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute(f"BEGIN {mode}")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _find_identifier(
        self,
        conn: sqlite3.Connection,
        producer: str,
        dataset: str,
        type: str,
        aggregationlevel: Optional[str],
        inventarisnummer: Optional[str],
        filepath: Optional[str]
    ) -> Optional[int]:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT unique_number FROM identifiers
            WHERE producer = ? AND dataset = ? AND type = ?
            AND aggregationlevel IS ? AND inventarisnummer IS ? AND filepath IS ?
        """, (producer, dataset, type, aggregationlevel, inventarisnummer, filepath))

        row = cursor.fetchone()

        return row['unique_number'] if row else None

    def _get_next_unique_number(
        self, conn: sqlite3.Connection, producer: str, dataset: str
    ) -> int:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT MAX(unique_number) as max_num FROM identifiers
            WHERE producer = ? AND dataset = ?
        """, (producer, dataset))

        row = cursor.fetchone()

        max_num = row['max_num'] if row and row['max_num'] is not None else 0
        return max_num + 1

    def _store_identifier(
        self,
        conn: sqlite3.Connection,
        producer: str,
        dataset: str,
        type: str,
        aggregationlevel: Optional[str],
        inventarisnummer: Optional[str],
        filepath: Optional[str],
        unique_number: int
    ):
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO identifiers
            (producer, dataset, type, aggregationlevel, inventarisnummer, filepath, unique_number)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (producer, dataset, type, aggregationlevel, inventarisnummer, filepath, unique_number))
