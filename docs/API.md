# API Documentation

This document provides detailed API documentation for all modules in the Excel to Streamlit MVP.

## Table of Contents

- [Logger Module](#logger-module)
- [Schema Detector Module](#schema-detector-module)
- [Database Manager Module](#database-manager-module)
- [CRUD Generator Module](#crud-generator-module)

## Logger Module

### `setup_logging(log_level: str = "INFO") -> None`

Set up logging configuration with file and console handlers.

**Parameters:**
- `log_level` (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to INFO.

**Example:**
```python
from src.logger import setup_logging
setup_logging("DEBUG")
```

### `get_logger(name: str) -> logging.Logger`

Get a logger for a specific module.

**Parameters:**
- `name` (str): Module name (typically `__name__`).

**Returns:**
- `logging.Logger`: Logger instance for the module.

**Example:**
```python
from src.logger import get_logger
logger = get_logger(__name__)
logger.info("This is a log message")
```

## Schema Detector Module

### `detect_schema(file_path: str) -> Dict[str, Any]`

Detect schema from Excel file (first sheet only).

**Parameters:**
- `file_path` (str): Path to the Excel file.

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `columns`: List of column names
  - `types`: Dictionary mapping column names to types (int, float, str, date)
  - `primary_key`: Name of primary key column (or 'id' if auto-generated)

**Raises:**
- `SchemaDetectionError`: If file cannot be read or has no data.

**Example:**
```python
from src.schema_detector import detect_schema
schema = detect_schema("data.xlsx")
print(schema["columns"])  # ['id', 'name', 'age']
print(schema["types"])    # {'id': 'int', 'name': 'str', 'age': 'int'}
print(schema["primary_key"])  # 'id'
```

### `clean_column_name(name: str) -> str`

Clean column name for SQL compatibility.

**Parameters:**
- `name` (str): Original column name.

**Returns:**
- `str`: Cleaned column name safe for SQL.

**Example:**
```python
from src.schema_detector import clean_column_name
cleaned = clean_column_name("Employee Name")  # "Employee_Name"
```

### `infer_column_types(df: pd.DataFrame) -> Dict[str, str]`

Infer column types from DataFrame.

**Parameters:**
- `df` (pd.DataFrame): DataFrame to analyze.

**Returns:**
- `Dict[str, str]`: Dictionary mapping column names to types (int, float, str, date).

### `detect_primary_key(df: pd.DataFrame, columns: List[str]) -> str`

Detect primary key column or generate one.

**Parameters:**
- `df` (pd.DataFrame): DataFrame to analyze.
- `columns` (List[str]): List of column names.

**Returns:**
- `str`: Name of primary key column.

## Database Manager Module

### `DatabaseManager(db_path: str = "data.db", table_name: str = "data")`

Manages SQLite database operations for a single table.

**Parameters:**
- `db_path` (str): Path to SQLite database file. Defaults to "data.db".
- `table_name` (str): Name of the table to manage. Defaults to "data".

**Example:**
```python
from src.db_manager import DatabaseManager
db = DatabaseManager(db_path="my_data.db", table_name="employees")
```

### `create_table(schema: Dict[str, Any]) -> None`

Create table from schema.

**Parameters:**
- `schema` (Dict[str, Any]): Schema dictionary with 'columns', 'types', and 'primary_key'.

**Raises:**
- `DatabaseError`: If table creation fails.

**Example:**
```python
schema = {
    "columns": ["id", "name", "age"],
    "types": {"id": "int", "name": "str", "age": "int"},
    "primary_key": "id"
}
db.create_table(schema)
```

### `insert_data(df: pd.DataFrame, schema: Dict[str, Any]) -> None`

Insert data from DataFrame into table.

**Parameters:**
- `df` (pd.DataFrame): DataFrame containing data to insert.
- `schema` (Dict[str, Any]): Schema dictionary.

**Raises:**
- `DatabaseError`: If insertion fails.

**Example:**
```python
import pandas as pd
df = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"], "age": [25, 30]})
db.insert_data(df, schema)
```

### `create_record(data: Dict[str, Any]) -> int`

Create a new record.

**Parameters:**
- `data` (Dict[str, Any]): Dictionary of column names to values.

**Returns:**
- `int`: ID of the created record (if auto-generated).

**Raises:**
- `DatabaseError`: If creation fails.

**Example:**
```python
record_id = db.create_record({"name": "Charlie", "age": 35})
print(record_id)  # 3
```

### `read_all() -> pd.DataFrame`

Read all records from table.

**Returns:**
- `pd.DataFrame`: DataFrame containing all records.

**Raises:**
- `DatabaseError`: If read fails.

**Example:**
```python
df = db.read_all()
print(df)
```

### `update_record(record_id: Any, data: Dict[str, Any]) -> None`

Update an existing record.

**Parameters:**
- `record_id` (Any): Primary key value of record to update.
- `data` (Dict[str, Any]): Dictionary of column names to new values.

**Raises:**
- `DatabaseError`: If update fails.

**Example:**
```python
db.update_record(1, {"name": "Alice Updated", "age": 26})
```

### `delete_record(record_id: Any) -> None`

Delete a record by ID.

**Parameters:**
- `record_id` (Any): Primary key value of record to delete.

**Raises:**
- `DatabaseError`: If deletion fails.

**Example:**
```python
db.delete_record(1)
```

## CRUD Generator Module

### `display_table_view(df: pd.DataFrame) -> None`

Display table view of all records.

**Parameters:**
- `df` (pd.DataFrame): DataFrame containing records to display.

**Example:**
```python
from src.crud_generator import display_table_view
display_table_view(df)
```

### `generate_create_form(schema: Dict[str, Any], db_manager: DatabaseManager) -> Optional[Dict[str, Any]]`

Generate and display create form.

**Parameters:**
- `schema` (Dict[str, Any]): Schema dictionary with 'columns' and 'types'.
- `db_manager` (DatabaseManager): DatabaseManager instance.

**Returns:**
- `Optional[Dict[str, Any]]`: Dictionary of form data if submitted, None otherwise.

### `generate_edit_form(schema: Dict[str, Any], df: pd.DataFrame, db_manager: DatabaseManager, primary_key: str) -> None`

Generate and display edit form.

**Parameters:**
- `schema` (Dict[str, Any]): Schema dictionary with 'columns' and 'types'.
- `df` (pd.DataFrame): DataFrame containing all records.
- `db_manager` (DatabaseManager): DatabaseManager instance.
- `primary_key` (str): Name of primary key column.

### `generate_delete_interface(df: pd.DataFrame, db_manager: DatabaseManager, primary_key: str) -> None`

Generate delete interface.

**Parameters:**
- `df` (pd.DataFrame): DataFrame containing all records.
- `db_manager` (DatabaseManager): DatabaseManager instance.
- `primary_key` (str): Name of primary key column.

### `render_crud_interface(schema: Dict[str, Any], db_manager: DatabaseManager) -> None`

Render complete CRUD interface.

**Parameters:**
- `schema` (Dict[str, Any]): Schema dictionary.
- `db_manager` (DatabaseManager): DatabaseManager instance.

**Example:**
```python
from src.crud_generator import render_crud_interface
render_crud_interface(schema, db_manager)
```
