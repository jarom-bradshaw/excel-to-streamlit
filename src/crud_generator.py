"""CRUD UI generator for Streamlit."""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
import logging

from src.logger import get_logger

logger = get_logger(__name__)


def display_table_view(df: pd.DataFrame) -> None:
    """
    Display table view of all records.

    Args:
        df: DataFrame containing records to display.
    """
    logger.debug(f"Displaying table view with {len(df)} records")
    if df.empty:
        st.info("No records found.")
        return

    st.dataframe(df, use_container_width=True, hide_index=True)


def generate_create_form(
    schema: Dict[str, Any], db_manager: Any
) -> Optional[Dict[str, Any]]:
    """
    Generate and display create form.

    Args:
        schema: Schema dictionary with 'columns' and 'types'.
        db_manager: DatabaseManager instance.

    Returns:
        Dictionary of form data if submitted, None otherwise.
    """
    logger.debug("Generating create form")

    st.subheader("Create New Record")

    with st.form("create_form"):
        form_data = {}
        columns = schema["columns"]
        types = schema["types"]
        primary_key = schema["primary_key"]

        # Generate input fields for each column (skip auto-generated id)
        for col in columns:
            if col == primary_key and primary_key == "id":
                continue  # Skip auto-generated primary key

            col_type = types.get(col, "str")

            if col_type == "int":
                form_data[col] = st.number_input(
                    col, value=0, step=1, key=f"create_{col}"
                )
            elif col_type == "float":
                form_data[col] = st.number_input(
                    col, value=0.0, step=0.01, key=f"create_{col}"
                )
            elif col_type == "date":
                form_data[col] = st.date_input(col, key=f"create_{col}")
            else:  # str
                form_data[col] = st.text_input(col, key=f"create_{col}")

        submitted = st.form_submit_button("Create Record")

        if submitted:
            try:
                # Convert date to string for storage
                for col, val in form_data.items():
                    if types.get(col) == "date" and val:
                        form_data[col] = val.isoformat()

                record_id = db_manager.create_record(form_data)
                logger.info(f"Created record with ID: {record_id}")
                st.success(f"Record created successfully! ID: {record_id}")
                st.rerun()
            except Exception as e:
                error_msg = f"Failed to create record: {e}"
                logger.error(error_msg, exc_info=True)
                st.error(error_msg)

    return None


def generate_edit_form(
    schema: Dict[str, Any],
    df: pd.DataFrame,
    db_manager: Any,
    primary_key: str,
) -> None:
    """
    Generate and display edit form.

    Args:
        schema: Schema dictionary with 'columns' and 'types'.
        df: DataFrame containing all records.
        db_manager: DatabaseManager instance.
        primary_key: Name of primary key column.
    """
    logger.debug("Generating edit form")

    st.subheader("Edit Record")

    if df.empty:
        st.info("No records available to edit.")
        return

    # Select record to edit
    if primary_key in df.columns:
        record_options = df[primary_key].astype(str).tolist()
        selected_key = st.selectbox(
            "Select record to edit",
            record_options,
            key="edit_select",
        )
        selected_record = df[df[primary_key].astype(str) == selected_key].iloc[0]
    else:
        st.error("Primary key column not found in data")
        return

    with st.form("edit_form"):
        form_data = {}
        columns = schema["columns"]
        types = schema["types"]

        # Generate input fields pre-filled with existing values
        for col in columns:
            if col == primary_key:
                # Display primary key as read-only
                st.text_input(col, value=str(selected_record[col]), disabled=True)
                form_data[col] = selected_record[col]
                continue

            col_type = types.get(col, "str")
            current_value = selected_record[col]

            if col_type == "int":
                form_data[col] = st.number_input(
                    col,
                    value=int(current_value) if pd.notna(current_value) else 0,
                    step=1,
                    key=f"edit_{col}",
                )
            elif col_type == "float":
                form_data[col] = st.number_input(
                    col,
                    value=float(current_value) if pd.notna(current_value) else 0.0,
                    step=0.01,
                    key=f"edit_{col}",
                )
            elif col_type == "date":
                # Parse date string if needed
                date_value = None
                if pd.notna(current_value):
                    try:
                        if isinstance(current_value, str):
                            date_value = pd.to_datetime(current_value).date()
                        else:
                            date_value = pd.to_datetime(current_value).date()
                    except Exception:
                        pass
                form_data[col] = st.date_input(
                    col, value=date_value, key=f"edit_{col}"
                )
            else:  # str
                form_data[col] = st.text_input(
                    col,
                    value=str(current_value) if pd.notna(current_value) else "",
                    key=f"edit_{col}",
                )

        submitted = st.form_submit_button("Update Record")

        if submitted:
            try:
                # Convert date to string for storage
                for col, val in form_data.items():
                    if types.get(col) == "date" and val:
                        form_data[col] = val.isoformat()

                record_id = selected_record[primary_key]
                db_manager.update_record(record_id, form_data)
                logger.info(f"Updated record {record_id}")
                st.success("Record updated successfully!")
                st.rerun()
            except Exception as e:
                error_msg = f"Failed to update record: {e}"
                logger.error(error_msg, exc_info=True)
                st.error(error_msg)


def generate_delete_interface(
    df: pd.DataFrame, db_manager: Any, primary_key: str
) -> None:
    """
    Generate delete interface.

    Args:
        df: DataFrame containing all records.
        db_manager: DatabaseManager instance.
        primary_key: Name of primary key column.
    """
    logger.debug("Generating delete interface")

    st.subheader("Delete Record")

    if df.empty:
        st.info("No records available to delete.")
        return

    if primary_key not in df.columns:
        st.error("Primary key column not found in data")
        return

    # Select record to delete
    record_options = df[primary_key].astype(str).tolist()
    selected_key = st.selectbox(
        "Select record to delete",
        record_options,
        key="delete_select",
    )

    # Confirmation
    if st.button("Delete Record", type="primary", key="delete_button"):
        try:
            # Get the actual primary key value (not string representation)
            selected_record = df[df[primary_key].astype(str) == selected_key].iloc[0]
            record_id = selected_record[primary_key]

            db_manager.delete_record(record_id)
            logger.info(f"Deleted record {record_id}")
            st.success("Record deleted successfully!")
            st.rerun()
        except Exception as e:
            error_msg = f"Failed to delete record: {e}"
            logger.error(error_msg, exc_info=True)
            st.error(error_msg)


def render_crud_interface(
    schema: Dict[str, Any], db_manager: Any
) -> None:
    """
    Render complete CRUD interface.

    Args:
        schema: Schema dictionary.
        db_manager: DatabaseManager instance.
    """
    logger.info("Rendering CRUD interface")

    # Read all records
    try:
        df = db_manager.read_all()
    except Exception as e:
        error_msg = f"Failed to read records: {e}"
        logger.error(error_msg, exc_info=True)
        st.error(error_msg)
        return

    primary_key = schema["primary_key"]

    # Create tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(["View", "Create", "Edit", "Delete"])

    with tab1:
        display_table_view(df)

    with tab2:
        generate_create_form(schema, db_manager)

    with tab3:
        generate_edit_form(schema, df, db_manager, primary_key)

    with tab4:
        generate_delete_interface(df, db_manager, primary_key)
