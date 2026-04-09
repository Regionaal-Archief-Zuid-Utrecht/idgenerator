import sqlite3
from pathlib import Path
from typing import Optional


class Database:
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
                aggregationlevel TEXT NOT NULL,
                inventarisnummer TEXT,
                filepath TEXT,
                unique_number INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(producer, dataset, type, aggregationlevel, inventarisnummer, filepath)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_producer_dataset 
            ON identifiers(producer, dataset)
        """)
        
        conn.commit()
        conn.close()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def find_identifier(
        self,
        producer: str,
        dataset: str,
        type: str,
        aggregationlevel: str,
        inventarisnummer: Optional[str],
        filepath: Optional[str]
    ) -> Optional[int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT unique_number FROM identifiers
            WHERE producer = ? AND dataset = ? AND type = ? 
            AND aggregationlevel = ? AND inventarisnummer IS ? AND filepath IS ?
        """, (producer, dataset, type, aggregationlevel, inventarisnummer, filepath))
        
        row = cursor.fetchone()
        conn.close()
        
        return row['unique_number'] if row else None

    def get_next_unique_number(self, producer: str, dataset: str) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT MAX(unique_number) as max_num FROM identifiers
            WHERE producer = ? AND dataset = ?
        """, (producer, dataset))
        
        row = cursor.fetchone()
        conn.close()
        
        max_num = row['max_num'] if row and row['max_num'] is not None else 0
        return max_num + 1

    def store_identifier(
        self,
        producer: str,
        dataset: str,
        type: str,
        aggregationlevel: str,
        inventarisnummer: Optional[str],
        filepath: Optional[str],
        unique_number: int
    ):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO identifiers 
                (producer, dataset, type, aggregationlevel, inventarisnummer, filepath, unique_number)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (producer, dataset, type, aggregationlevel, inventarisnummer, filepath, unique_number))
            
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()
