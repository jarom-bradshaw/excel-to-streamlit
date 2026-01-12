"""Schema detection module for Excel files."""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from src.logger import get_logger

logger = get_logger(__name__)


class SchemaDetectionError(Exception):
    """Custom exception for schema detection errors."""

    pass


def detect_schema(file_path: str) -> Dict[str, Any]:
    """
    Detect schema from Excel file (first sheet only).

    Args:
        file_path: Path to the Excel file.

    Returns:
        Dictionary containing:
        - columns: List of column names
        - types: Dictionary mapping column names to types (int, float, str, date)
        - primary_key: Name of primary key column (or 'id' if auto-generated)

    Raises:
        SchemaDetectionError: If file cannot be read or has no data.
    """
    logger.info(f"Starting schema detection for file: {file_path}")

    try:
        # Read first sheet only
        df = pd.read_excel(file_path, sheet_name=0, engine=None)
        logger.debug(f"Read {len(df)} rows, {len(df.columns)} columns")

        if df.empty:
            raise SchemaDetectionError("Excel file contains no data")

        if len(df.columns) == 0:
            raise SchemaDetectionError("Excel file has no columns")

        # Handle missing headers
        if df.columns[0].startswith("Unnamed"):
            logger.warning("No headers detected, auto-generating column names")
            df.columns = [f"Column{i+1}" for i in range(len(df.columns))]

        # Clean column names (remove invalid characters for SQL)
        columns = [clean_column_name(col) for col in df.columns]
        df.columns = columns

        # Infer column types
        types = infer_column_types(df)
        logger.debug(f"Inferred types: {types}")

        # Detect primary key
        primary_key = detect_primary_key(df, columns)
        logger.info(
            f"Schema detected: {len(columns)} columns, PK: {primary_key}"
        )

        return {
            "columns": columns,
            "types": types,
            "primary_key": primary_key,
        }

    except pd.errors.EmptyDataError:
        error_msg = "Excel file is empty"
        logger.error(error_msg)
        raise SchemaDetectionError(error_msg)
    except pd.errors.ParserError as e:
        error_msg = f"Error parsing Excel file: {e}"
        logger.error(error_msg, exc_info=True)
        raise SchemaDetectionError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error during schema detection: {e}"
        logger.error(error_msg, exc_info=True)
        raise SchemaDetectionError(error_msg)


def clean_column_name(name: str) -> str:
    """
    Clean column name for SQL compatibility.

    Args:
        name: Original column name.

    Returns:
        Cleaned column name safe for SQL.
    """
    # Replace spaces and special characters with underscores
    cleaned = str(name).strip().replace(" ", "_")
    # Remove invalid SQL characters
    cleaned = "".join(c if c.isalnum() or c == "_" else "_" for c in cleaned)
    # Ensure it doesn't start with a number
    if cleaned and cleaned[0].isdigit():
        cleaned = f"col_{cleaned}"
    # Ensure it's not empty
    if not cleaned:
        cleaned = "Column_A"
    return cleaned


def infer_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Infer column types from DataFrame.

    Args:
        df: DataFrame to analyze.

    Returns:
        Dictionary mapping column names to types (int, float, str, date).
    """
    types = {}

    for col in df.columns:
        # Skip null-only columns
        if df[col].isna().all():
            types[col] = "str"
            logger.debug(f"Column '{col}' is all null, defaulting to str")
            continue

        # Check for date/datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            types[col] = "date"
            continue

        # Try to infer from non-null values
        non_null = df[col].dropna()

        if len(non_null) == 0:
            types[col] = "str"
            continue

        # Check if all values are integers
        if pd.api.types.is_integer_dtype(non_null):
            types[col] = "int"
        # Check if all values are floats
        elif pd.api.types.is_float_dtype(non_null):
            types[col] = "float"
        # Check if can be converted to date
        elif is_date_column(non_null):
            types[col] = "date"
        # Default to string
        else:
            types[col] = "str"

    return types


def is_date_column(series: pd.Series) -> bool:
    """
    Check if a series contains date-like values.

    Args:
        series: Series to check.

    Returns:
        True if series appears to contain dates.
    """
    # Try to convert to datetime
    try:
        pd.to_datetime(series, errors="raise")
        return True
    except (ValueError, TypeError):
        return False


def detect_primary_key(df: pd.DataFrame, columns: List[str]) -> str:
    """
    Detect primary key column or generate one.

    Args:
        df: DataFrame to analyze.
        columns: List of column names.

    Returns:
        Name of primary key column.
    """
    if not columns:
        logger.warning("No columns found, generating 'id' as primary key")
        return "id"

    # Check if first column is unique
    first_col = columns[0]
    if df[first_col].notna().any():
        unique_count = df[first_col].nunique()
        total_count = len(df[first_col].dropna())

        if unique_count == total_count and total_count > 0:
            logger.info(f"Using '{first_col}' as primary key (unique column)")
            return first_col

    # Check other columns for uniqueness
    for col in columns:
        if col == first_col:
            continue
        if df[col].notna().any():
            unique_count = df[col].nunique()
            total_count = len(df[col].dropna())
            if unique_count == total_count and total_count > 0:
                logger.info(f"Using '{col}' as primary key (unique column)")
                return col

    # No unique column found, generate id
    logger.warning("No unique column found, will auto-generate 'id' as primary key")
    return "id"
