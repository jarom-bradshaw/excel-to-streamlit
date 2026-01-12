"""Unit tests for schema_detector module."""

import pytest
import pandas as pd
from pathlib import Path
from src.schema_detector import (
    detect_schema,
    clean_column_name,
    infer_column_types,
    is_date_column,
    detect_primary_key,
    SchemaDetectionError,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestSchemaDetection:
    """Test schema detection functionality."""

    def test_detect_schema_basic(self):
        """Test basic schema detection with all column types."""
        file_path = str(FIXTURES_DIR / "sample_data.xlsx")
        schema = detect_schema(file_path)

        assert "columns" in schema
        assert "types" in schema
        assert "primary_key" in schema
        assert len(schema["columns"]) == 5
        assert schema["primary_key"] == "id"

    def test_detect_schema_no_headers(self):
        """Test schema detection with missing headers."""
        file_path = str(FIXTURES_DIR / "sample_no_headers.xlsx")
        schema = detect_schema(file_path)

        assert len(schema["columns"]) > 0
        # Should auto-generate column names
        assert any(col.startswith("Column") for col in schema["columns"])

    def test_detect_schema_no_pk(self):
        """Test schema detection without unique primary key."""
        file_path = str(FIXTURES_DIR / "sample_no_pk.xlsx")
        schema = detect_schema(file_path)

        assert schema["primary_key"] == "id"  # Should auto-generate

    def test_detect_schema_empty_file(self):
        """Test schema detection with empty file."""
        file_path = str(FIXTURES_DIR / "sample_empty.xlsx")
        with pytest.raises(SchemaDetectionError):
            detect_schema(file_path)

    def test_detect_schema_nonexistent_file(self):
        """Test schema detection with nonexistent file."""
        with pytest.raises(SchemaDetectionError):
            detect_schema("nonexistent.xlsx")


class TestColumnNameCleaning:
    """Test column name cleaning functionality."""

    def test_clean_column_name_basic(self):
        """Test basic column name cleaning."""
        assert clean_column_name("Name") == "Name"
        assert clean_column_name("Employee Name") == "Employee_Name"

    def test_clean_column_name_special_chars(self):
        """Test cleaning special characters."""
        assert clean_column_name("Name@#$") == "Name___"
        assert clean_column_name("123Name") == "col_123Name"

    def test_clean_column_name_empty(self):
        """Test cleaning empty column name."""
        result = clean_column_name("")
        assert result == "Column_A"


class TestTypeInference:
    """Test column type inference."""

    def test_infer_column_types(self):
        """Test type inference for different data types."""
        df = pd.DataFrame({
            "int_col": [1, 2, 3],
            "float_col": [1.5, 2.5, 3.5],
            "str_col": ["a", "b", "c"],
            "date_col": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
        })

        types = infer_column_types(df)
        assert types["int_col"] == "int"
        assert types["float_col"] == "float"
        assert types["str_col"] == "str"
        assert types["date_col"] == "date"

    def test_infer_column_types_mixed(self):
        """Test type inference with mixed types (should default to str)."""
        df = pd.DataFrame({
            "mixed_col": [1, "text", 3.5],
        })

        types = infer_column_types(df)
        assert types["mixed_col"] == "str"


class TestDateDetection:
    """Test date column detection."""

    def test_is_date_column_valid(self):
        """Test valid date column detection."""
        series = pd.Series(pd.to_datetime(["2020-01-01", "2020-01-02"]))
        assert is_date_column(series) is True

    def test_is_date_column_invalid(self):
        """Test invalid date column detection."""
        series = pd.Series([1, 2, 3])
        assert is_date_column(series) is False


class TestPrimaryKeyDetection:
    """Test primary key detection."""

    def test_detect_primary_key_unique_first(self):
        """Test primary key detection with unique first column."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["A", "B", "C"],
        })
        pk = detect_primary_key(df, ["id", "name"])
        assert pk == "id"

    def test_detect_primary_key_unique_other(self):
        """Test primary key detection with unique other column."""
        df = pd.DataFrame({
            "category": ["A", "A", "B"],
            "id": [1, 2, 3],
        })
        pk = detect_primary_key(df, ["category", "id"])
        assert pk == "id"

    def test_detect_primary_key_no_unique(self):
        """Test primary key detection with no unique column."""
        df = pd.DataFrame({
            "category": ["A", "A", "B"],
            "value": [1, 2, 3],
        })
        pk = detect_primary_key(df, ["category", "value"])
        assert pk == "id"  # Should auto-generate
