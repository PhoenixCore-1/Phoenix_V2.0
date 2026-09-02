"""Minimal SQLite infrastructure for the first V2 vertical slice."""

import sqlite3
from pathlib import Path

SCHEMA = Path(__file__).resolve().parents[2] / "migrations" / "001_core_foundation.sql"

class SQLiteDatabase:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def close(self):
        self.connection.close()

    def execute(self, sql, params=()):
        return self.connection.execute(sql, params)

    def executescript(self, sql):
        return self.connection.executescript(sql)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def integrity_check(self) -> bool:
        row = self.connection.execute("PRAGMA integrity_check").fetchone()
        return row[0] == "ok"
