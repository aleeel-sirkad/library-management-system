"""
Database module for the Library Management System.

Handles SQLite connection management and automatic database initialization.
"""

import sqlite3
from pathlib import Path
from typing import Optional


# Default path to the SQLite database file
DEFAULT_DB_PATH = Path(__file__).parent / "database" / "library.db"
DEFAULT_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class DatabaseError(Exception):
    """Raised when a database operation fails."""

    pass


class DatabaseManager:
  """
  Manages SQLite database connections and schema initialization.

  Creates the database file and tables automatically on first use.
  """

  def __init__(self, db_path: Optional[str] = None, schema_path: Optional[str] = None):
    """
    Initialize the database manager.

    Args:
        db_path: Path to the SQLite database file. Uses default if not provided.
        schema_path: Path to the SQL schema file. Uses default if not provided.
    """
    self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
    self.schema_path = Path(schema_path) if schema_path else DEFAULT_SCHEMA_PATH
    self._ensure_database_directory()
    self.initialize_database()

  def _ensure_database_directory(self) -> None:
    """Create the database directory if it does not exist."""
    self.db_path.parent.mkdir(parents=True, exist_ok=True)

  def get_connection(self) -> sqlite3.Connection:
    """
    Return a new database connection with foreign keys enabled.

    Returns:
        sqlite3.Connection: Active database connection.
    """
    try:
      conn = sqlite3.connect(self.db_path)
      conn.row_factory = sqlite3.Row
      conn.execute("PRAGMA foreign_keys = ON")
      return conn
    except sqlite3.Error as exc:
      raise DatabaseError(f"Failed to connect to database: {exc}") from exc

  def initialize_database(self) -> None:
    """
    Create tables from schema.sql if they do not already exist.

    Raises:
        DatabaseError: If schema file is missing or execution fails.
    """
    if not self.schema_path.exists():
      raise DatabaseError(f"Schema file not found: {self.schema_path}")

    try:
      with open(self.schema_path, "r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()

      with self.get_connection() as conn:
        conn.executescript(schema_sql)
        conn.commit()
    except sqlite3.Error as exc:
      raise DatabaseError(f"Failed to initialize database: {exc}") from exc
    except OSError as exc:
      raise DatabaseError(f"Failed to read schema file: {exc}") from exc
