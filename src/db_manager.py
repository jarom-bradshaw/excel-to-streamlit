"""Database manager for SQLite operations."""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
import logging

from src.logger import get_logger

logger = get_logger(__name__)


class DatabaseError(Exception):
    """Custom exception for database errors."""

    pass


class DatabaseManager:
    """Manages SQLite database operations for a single table."""

    def __init__(self, db_path: str = "data.db", table_name: str = "data"):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file.
            table_name: Name of the table to manage.
        """
        self.db_path = db_path
        self.table_name = table_name
        logger.info(f"DatabaseManager initialized: db={db_path}, table={table_name}")

    @contextmanager
    def get_connection(self):
        """
        Get database connection as context manager.

        Yields:
            SQLite connection object.
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}", exc_info=True)
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            if conn:
                conn.close()

    def create_table(self, schema: Dict[str, Any]) -> None:
        """
        Create table from schema.

        Args:
            schema: Schema dictionary with 'columns', 'types', and 'primary_key'.

        Raises:
            DatabaseError: If table creation fails.
        """
        logger.info(f"Creating table '{self.table_name}' with schema")
        columns = schema["columns"]
        types = schema["types"]
        primary_key = schema["primary_key"]

        # Build column definitions
        col_defs = []
        for col in columns:
            col_type = self._map_type_to_sqlite(types.get(col, "str"))
            if col == primary_key:
                if primary_key == "id":
                    # Auto-increment integer primary key
                    col_defs.append(f"{col} INTEGER PRIMARY KEY AUTOINCREMENT")
                else:
                    # Use existing column as primary key
                    col_defs.append(f"{col} {col_type} PRIMARY KEY")
            else:
                col_defs.append(f"{col} {col_type}")

        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            {', '.join(col_defs)}
        )
        """

        try:
            with self.get_connection() as conn:
                conn.execute(create_sql)
                logger.info(f"Table '{self.table_name}' created successfully")
        except sqlite3.Error as e:
            error_msg = f"Failed to create table: {e}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseError(error_msg)

    def _map_type_to_sqlite(self, python_type: str) -> str:
        """
        Map Python type to SQLite type.

        Args:
            python_type: Python type string (int, float, str, date).

        Returns:
            SQLite type string.
        """
        type_mapping = {
            "int": "INTEGER",
            "float": "REAL",
            "str": "TEXT",
            "date": "TEXT",  # Store dates as ISO format strings
        }
        return type_mapping.get(python_type, "TEXT")

    def insert_data(self, df: pd.DataFrame, schema: Dict[str, Any]) -> None:
        """
        Insert data from DataFrame into table.

        Args:
            df: DataFrame containing data to insert.
            schema: Schema dictionary.

        Raises:
            DatabaseError: If insertion fails.
        """
        logger.info(f"Inserting {len(df)} rows into '{self.table_name}'")

        # Handle auto-generated primary key
        primary_key = schema["primary_key"]
        if primary_key == "id" and "id" not in df.columns:
            # Don't include id column in insert (auto-generated)
            insert_columns = [col for col in df.columns if col != "id"]
        else:
            insert_columns = df.columns.tolist()

        # Prepare data for insertion
        placeholders = ", ".join(["?" for _ in insert_columns])
        columns_str = ", ".join(insert_columns)
        insert_sql = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders})"

        try:
            with self.get_connection() as conn:
                # Convert DataFrame to list of tuples
                data_to_insert = []
                for _, row in df.iterrows():
                    values = []
                    for col in insert_columns:
                        val = row[col]
                        # Convert dates to ISO format strings
                        if pd.isna(val):
                            values.append(None)
                        elif isinstance(val, pd.Timestamp):
                            values.append(val.isoformat())
                        else:
                            values.append(val)
                    data_to_insert.append(tuple(values))

                conn.executemany(insert_sql, data_to_insert)
                logger.info(f"Successfully inserted {len(data_to_insert)} rows")
        except sqlite3.Error as e:
            error_msg = f"Failed to insert data: {e}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseError(error_msg)

    def create_record(self, data: Dict[str, Any]) -> int:
        """
        Create a new record.

        Args:
            data: Dictionary of column names to values.

        Returns:
            ID of the created record (if auto-generated).

        Raises:
            DatabaseError: If creation fails.
        """
        logger.debug(f"Creating record in '{self.table_name}': {data}")

        columns = list(data.keys())
        placeholders = ", ".join(["?" for _ in columns])
        columns_str = ", ".join(columns)
        insert_sql = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders})"

        try:
            with self.get_connection() as conn:
                values = [data[col] for col in columns]
                cursor = conn.execute(insert_sql, values)
                record_id = cursor.lastrowid
                logger.info(f"Created record with ID: {record_id}")
                return record_id
        except sqlite3.Error as e:
            error_msg = f"Failed to create record: {e}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseError(error_msg)

    def read_all(self) -> pd.DataFrame:
        """
        Read all records from table.

        Returns:
            DataFrame containing all records.

        Raises:
            DatabaseError: If read fails.
        """
        logger.debug(f"Reading all records from '{self.table_name}'")

        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(f"SELECT * FROM {self.table_name}", conn)
                logger.info(f"Read {len(df)} records")
                return df
        except sqlite3.Error as e:
            error_msg = f"Failed to read records: {e}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseError(error_msg)

    def update_record(self, record_id: Any, data: Dict[str, Any]) -> None:
        """
        Update an existing record.

        Args:
            record_id: Primary key value of record to update.
            data: Dictionary of column names to new values.

        Raises:
            DatabaseError: If update fails.
        """
        logger.debug(f"Updating record {record_id} in '{self.table_name}': {data}")

        # Get primary key column name (assume it's 'id' or first column)
        # For simplicity, we'll use the first key in data or 'id'
        primary_key = "id" if "id" in data else list(data.keys())[0]

        set_clauses = [f"{col} = ?" for col in data.keys() if col != primary_key]
        if not set_clauses:
            logger.warning("No fields to update")
            return

        update_sql = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE {primary_key} = ?"

        try:
            with self.get_connection() as conn:
                values = [data[col] for col in data.keys() if col != primary_key]
                values.append(record_id)
                conn.execute(update_sql, values)
                logger.info(f"Updated record {record_id}")
        except sqlite3.Error as e:
            error_msg = f"Failed to update record: {e}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseError(error_msg)

    def delete_record(self, record_id: Any) -> None:
        """
        Delete a record by ID.

        Args:
            record_id: Primary key value of record to delete.

        Raises:
            DatabaseError: If deletion fails.
        """
        logger.debug(f"Deleting record {record_id} from '{self.table_name}'")

        # Try 'id' first, then assume first column is primary key
        delete_sql = f"DELETE FROM {self.table_name} WHERE id = ?"

        try:
            with self.get_connection() as conn:
                cursor = conn.execute(delete_sql, (record_id,))
                if cursor.rowcount == 0:
                    # Try with first column as primary key
                    # Get table info to find primary key
                    cursor = conn.execute(f"PRAGMA table_info({self.table_name})")
                    table_info = cursor.fetchall()
                    if table_info:
                        pk_col = next(
                            (row[1] for row in table_info if row[5] == 1),
                            table_info[0][1],
                        )
                        delete_sql = f"DELETE FROM {self.table_name} WHERE {pk_col} = ?"
                        conn.execute(delete_sql, (record_id,))
                logger.info(f"Deleted record {record_id}")
        except sqlite3.Error as e:
            error_msg = f"Failed to delete record: {e}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseError(error_msg)
