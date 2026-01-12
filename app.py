"""Main Streamlit application for Excel to Streamlit MVP."""

import streamlit as st
import pandas as pd
import tempfile
import os
from pathlib import Path
from typing import Optional, Tuple

from src.logger import setup_logging, get_logger
from src.schema_detector import detect_schema, SchemaDetectionError
from src.db_manager import DatabaseManager, DatabaseError
from src.crud_generator import render_crud_interface

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Excel to Streamlit MVP",
    page_icon="📊",
    layout="wide",
)

# Constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_ROWS = 10000
SUPPORTED_EXTENSIONS = [".xlsx", ".xls"]


def validate_file(uploaded_file) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file.

    Args:
        uploaded_file: Streamlit uploaded file object.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if uploaded_file is None:
        return False, None

    # Check file extension
    file_ext = Path(uploaded_file.name).suffix.lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        return False, f"Unsupported file format. Only {', '.join(SUPPORTED_EXTENSIONS)} files are supported."

    # Check file size
    if uploaded_file.size > MAX_FILE_SIZE:
        return False, f"File exceeds {MAX_FILE_SIZE / (1024*1024):.0f}MB limit. Please use a smaller file."

    return True, None


def process_excel_file(uploaded_file) -> Tuple[Optional[dict], Optional[str]]:
    """
    Process uploaded Excel file.

    Args:
        uploaded_file: Streamlit uploaded file object.

    Returns:
        Tuple of (schema_dict, error_message).
    """
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            # Detect schema
            logger.info(f"Processing file: {uploaded_file.name}")
            schema = detect_schema(tmp_path)

            # Read data
            df = pd.read_excel(tmp_path, sheet_name=0, engine=None)

            # Check row count
            if len(df) > MAX_ROWS:
                return None, f"Sheet exceeds {MAX_ROWS} row limit. Please use a smaller dataset for MVP."

            # Create database and load data
            db_manager = DatabaseManager(table_name="data")
            db_manager.create_table(schema)
            db_manager.insert_data(df, schema)

            logger.info(f"Successfully processed file: {uploaded_file.name}, {len(df)} rows")

            return schema, None

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except SchemaDetectionError as e:
        error_msg = str(e)
        logger.error(f"Schema detection error: {error_msg}")
        return None, error_msg
    except pd.errors.EmptyDataError:
        error_msg = "Excel file is empty or contains no data."
        logger.error(error_msg)
        return None, error_msg
    except pd.errors.ParserError as e:
        error_msg = f"Error parsing Excel file: {e}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg
    except Exception as e:
        error_msg = f"Unexpected error processing file: {e}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg


def main():
    """Main application function."""
    st.title("📊 Excel to Streamlit MVP")
    st.markdown("Upload an Excel file to generate a CRUD interface")

    # Initialize session state
    if "schema" not in st.session_state:
        st.session_state.schema = None
    if "db_manager" not in st.session_state:
        st.session_state.db_manager = None

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=["xlsx", "xls"],
        help="Upload a .xlsx or .xls file (first sheet only, max 50MB, max 10,000 rows)",
    )

    if uploaded_file is not None:
        # Validate file
        is_valid, error_msg = validate_file(uploaded_file)
        if not is_valid:
            if error_msg:
                st.error(error_msg)
            return

        # Process file if not already processed
        if st.session_state.schema is None or st.button("Re-upload File"):
            with st.spinner("Processing file..."):
                schema, error_msg = process_excel_file(uploaded_file)

                if error_msg:
                    st.error(error_msg)
                    st.session_state.schema = None
                    st.session_state.db_manager = None
                else:
                    st.session_state.schema = schema
                    st.session_state.db_manager = DatabaseManager(table_name="data")
                    # Get record count from database
                    try:
                        df = st.session_state.db_manager.read_all()
                        record_count = len(df)
                    except Exception:
                        record_count = 0
                    st.success(f"File processed successfully! Loaded {record_count} records.")
                    st.rerun()

    # Display CRUD interface if schema is available
    if st.session_state.schema is not None and st.session_state.db_manager is not None:
        st.divider()
        render_crud_interface(st.session_state.schema, st.session_state.db_manager)
    elif uploaded_file is None:
        st.info("👆 Please upload an Excel file to get started")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Application error: {e}", exc_info=True)
        st.error(f"An unexpected error occurred: {e}")
        st.info("Please check the logs for more details.")
