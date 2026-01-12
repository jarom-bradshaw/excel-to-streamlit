"""Unit tests for db_manager module."""

import pytest
import pandas as pd
import sqlite3
import tempfile
import os
from src.db_manager import DatabaseManager, DatabaseError

# Use in-memory database for tests
TEST_DB = ":memory:"


class TestDatabaseManager:
    """Test DatabaseManager functionality."""

    def setup_method(self):
        """Set up test database manager."""
        self.db_manager = DatabaseManager(db_path=TEST_DB, table_name="test_data")

    def test_create_table(self):
        """Test table creation."""
        schema = {
            "columns": ["id", "name", "age"],
            "types": {"id": "int", "name": "str", "age": "int"},
            "primary_key": "id",
        }
        self.db_manager.create_table(schema)

        # Verify table exists
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='test_data'"
            )
            assert cursor.fetchone() is not None

    def test_create_table_auto_id(self):
        """Test table creation with auto-generated ID."""
        schema = {
            "columns": ["id", "name"],
            "types": {"id": "int", "name": "str"},
            "primary_key": "id",
        }
        self.db_manager.create_table(schema)

    def test_insert_data(self):
        """Test data insertion."""
        schema = {
            "columns": ["id", "name", "age"],
            "types": {"id": "int", "name": "str", "age": "int"},
            "primary_key": "id",
        }
        self.db_manager.create_table(schema)

        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
        })
        self.db_manager.insert_data(df, schema)

        # Verify data
        result_df = self.db_manager.read_all()
        assert len(result_df) == 3
        assert result_df["name"].iloc[0] == "Alice"

    def test_insert_data_auto_id(self):
        """Test data insertion with auto-generated ID."""
        schema = {
            "columns": ["id", "name"],
            "types": {"id": "int", "name": "str"},
            "primary_key": "id",
        }
        self.db_manager.create_table(schema)

        df = pd.DataFrame({
            "name": ["Alice", "Bob"],
        })
        self.db_manager.insert_data(df, schema)

        result_df = self.db_manager.read_all()
        assert len(result_df) == 2
        assert "id" in result_df.columns

    def test_create_record(self):
        """Test creating a single record."""
        schema = {
            "columns": ["id", "name", "age"],
            "types": {"id": "int", "name": "str", "age": "int"},
            "primary_key": "id",
        }
        self.db_manager.create_table(schema)

        record_id = self.db_manager.create_record({
            "id": 1,
            "name": "Alice",
            "age": 25,
        })
        assert record_id == 1

    def test_read_all(self):
        """Test reading all records."""
        schema = {
            "columns": ["id", "name"],
            "types": {"id": "int", "name": "str"},
            "primary_key": "id",
        }
        self.db_manager.create_table(schema)

        self.db_manager.create_record({"id": 1, "name": "Alice"})
        self.db_manager.create_record({"id": 2, "name": "Bob"})

        df = self.db_manager.read_all()
        assert len(df) == 2
        assert "name" in df.columns

    def test_update_record(self):
        """Test updating a record."""
        schema = {
            "columns": ["id", "name", "age"],
            "types": {"id": "int", "name": "str", "age": "int"},
            "primary_key": "id",
        }
        self.db_manager.create_table(schema)

        self.db_manager.create_record({"id": 1, "name": "Alice", "age": 25})
        self.db_manager.update_record(1, {"name": "Alice Updated", "age": 26})

        df = self.db_manager.read_all()
        assert df[df["id"] == 1]["name"].iloc[0] == "Alice Updated"

    def test_delete_record(self):
        """Test deleting a record."""
        schema = {
            "columns": ["id", "name"],
            "types": {"id": "int", "name": "str"},
            "primary_key": "id",
        }
        self.db_manager.create_table(schema)

        self.db_manager.create_record({"id": 1, "name": "Alice"})
        self.db_manager.create_record({"id": 2, "name": "Bob"})

        self.db_manager.delete_record(1)

        df = self.db_manager.read_all()
        assert len(df) == 1
        assert df["name"].iloc[0] == "Bob"

    def test_connection_context_manager(self):
        """Test connection context manager."""
        with self.db_manager.get_connection() as conn:
            assert conn is not None
            # Connection should be closed after context
