"""Unit tests for main Streamlit app."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Import app functions
from app import validate_file, process_excel_file

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestFileValidation:
    """Test file validation functionality."""

    def test_validate_file_valid(self):
        """Test validation of valid file."""
        mock_file = Mock()
        mock_file.name = "test.xlsx"
        mock_file.size = 1024  # 1KB

        is_valid, error = validate_file(mock_file)
        assert is_valid is True
        assert error is None

    def test_validate_file_invalid_extension(self):
        """Test validation of file with invalid extension."""
        mock_file = Mock()
        mock_file.name = "test.pdf"
        mock_file.size = 1024

        is_valid, error = validate_file(mock_file)
        assert is_valid is False
        assert error is not None

    def test_validate_file_too_large(self):
        """Test validation of file that's too large."""
        mock_file = Mock()
        mock_file.name = "test.xlsx"
        mock_file.size = 100 * 1024 * 1024  # 100MB

        is_valid, error = validate_file(mock_file)
        assert is_valid is False
        assert "exceeds" in error.lower()

    def test_validate_file_none(self):
        """Test validation of None file."""
        is_valid, error = validate_file(None)
        assert is_valid is False
        assert error is None


class TestProcessExcelFile:
    """Test Excel file processing."""

    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.detect_schema')
    @patch('app.pd.read_excel')
    @patch('app.DatabaseManager')
    def test_process_excel_file_success(self, mock_db, mock_read_excel, mock_detect, mock_tempfile):
        """Test successful file processing."""
        # Setup mocks
        mock_file = Mock()
        mock_file.name = "test.xlsx"
        mock_file.getvalue.return_value = b"fake excel data"

        mock_temp = Mock()
        mock_temp.__enter__.return_value = mock_temp
        mock_temp.__exit__.return_value = None
        mock_temp.name = "/tmp/test.xlsx"
        mock_tempfile.return_value = mock_temp

        mock_detect.return_value = {
            "columns": ["id", "name"],
            "types": {"id": "int", "name": "str"},
            "primary_key": "id",
        }

        mock_df = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
        mock_read_excel.return_value = mock_df

        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance

        schema, error = process_excel_file(mock_file)

        assert schema is not None
        assert error is None
        assert mock_detect.called
        assert mock_db_instance.create_table.called
        assert mock_db_instance.insert_data.called

    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.detect_schema')
    def test_process_excel_file_schema_error(self, mock_detect, mock_tempfile):
        """Test file processing with schema detection error."""
        from src.schema_detector import SchemaDetectionError

        mock_file = Mock()
        mock_file.name = "test.xlsx"
        mock_file.getvalue.return_value = b"fake excel data"

        mock_temp = Mock()
        mock_temp.__enter__.return_value = mock_temp
        mock_temp.__exit__.return_value = None
        mock_temp.name = "/tmp/test.xlsx"
        mock_tempfile.return_value = mock_temp

        mock_detect.side_effect = SchemaDetectionError("Test error")

        schema, error = process_excel_file(mock_file)

        assert schema is None
        assert error is not None
        assert "test error" in error.lower()
