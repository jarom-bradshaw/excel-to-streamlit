"""Unit tests for crud_generator module."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import streamlit as st

# Mock streamlit before importing crud_generator
import sys
from io import StringIO

# Create a mock streamlit module
mock_streamlit = Mock()
sys.modules['streamlit'] = mock_streamlit

from src.crud_generator import (
    display_table_view,
    generate_create_form,
    generate_edit_form,
    generate_delete_interface,
    render_crud_interface,
)


class TestDisplayTableView:
    """Test table view display."""

    @patch('src.crud_generator.st')
    def test_display_table_view_with_data(self, mock_st):
        """Test displaying table with data."""
        df = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
        display_table_view(df)
        mock_st.dataframe.assert_called_once()

    @patch('src.crud_generator.st')
    def test_display_table_view_empty(self, mock_st):
        """Test displaying empty table."""
        df = pd.DataFrame()
        display_table_view(df)
        mock_st.info.assert_called_once()


class TestCreateForm:
    """Test create form generation."""

    @patch('src.crud_generator.st')
    def test_generate_create_form(self, mock_st):
        """Test create form generation."""
        schema = {
            "columns": ["id", "name", "age"],
            "types": {"id": "int", "name": "str", "age": "int"},
            "primary_key": "id",
        }
        db_manager = Mock()
        db_manager.create_record.return_value = 1

        # Mock form submission
        mock_st.form.return_value.__enter__.return_value = Mock()
        mock_st.form_submit_button.return_value = True

        result = generate_create_form(schema, db_manager)
        # Should return None (form handling is async in Streamlit)
        assert result is None


class TestEditForm:
    """Test edit form generation."""

    @patch('src.crud_generator.st')
    def test_generate_edit_form(self, mock_st):
        """Test edit form generation."""
        schema = {
            "columns": ["id", "name"],
            "types": {"id": "int", "name": "str"},
            "primary_key": "id",
        }
        df = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
        db_manager = Mock()

        # Mock selectbox
        mock_st.selectbox.return_value = "1"

        generate_edit_form(schema, df, db_manager, "id")
        # Should not raise exception


class TestDeleteInterface:
    """Test delete interface generation."""

    @patch('src.crud_generator.st')
    def test_generate_delete_interface(self, mock_st):
        """Test delete interface generation."""
        df = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
        db_manager = Mock()

        # Mock selectbox and button
        mock_st.selectbox.return_value = "1"
        mock_st.button.return_value = False

        generate_delete_interface(df, db_manager, "id")
        # Should not raise exception

    @patch('src.crud_generator.st')
    def test_generate_delete_interface_empty(self, mock_st):
        """Test delete interface with empty data."""
        df = pd.DataFrame()
        db_manager = Mock()

        generate_delete_interface(df, db_manager, "id")
        mock_st.info.assert_called_once()
