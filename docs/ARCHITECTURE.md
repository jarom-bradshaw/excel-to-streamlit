# Architecture Documentation

This document describes the architecture, design decisions, and data flow of the Excel to Streamlit MVP.

## System Overview

The application follows a modular architecture with clear separation of concerns:

1. **Schema Detection**: Analyzes Excel files and infers data structure
2. **Database Management**: Handles SQLite operations
3. **UI Generation**: Creates Streamlit interface components
4. **Main Application**: Orchestrates the workflow

## Architecture Diagram

```
┌─────────────────┐
│   Excel File    │
│   (.xlsx/.xls)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Schema Detector│
│  - Read Excel   │
│  - Infer types  │
│  - Detect PK    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Database Manager │
│  - Create table  │
│  - Insert data   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CRUD Generator  │
│  - Generate UI   │
│  - Handle forms  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Streamlit UI   │
│  - View/CRUD    │
└─────────────────┘
```

## Data Flow

### 1. File Upload
- User uploads Excel file through Streamlit file uploader
- File is validated (extension, size)
- File is saved to temporary location

### 2. Schema Detection
- Excel file is read using pandas (first sheet only)
- Column types are inferred (int, float, str, date)
- Primary key is detected (unique column or auto-generated)
- Schema dictionary is returned

### 3. Database Creation
- SQLite table is created based on schema
- Column types are mapped to SQLite types
- Primary key constraints are applied

### 4. Data Loading
- DataFrame is read from Excel
- Data is inserted into SQLite table
- Auto-generated IDs are handled if needed

### 5. UI Generation
- CRUD interface is generated based on schema
- Forms are dynamically created with appropriate input types
- Table view displays all records

### 6. User Interactions
- Create: New records are inserted via form
- Read: All records are displayed in table
- Update: Existing records are modified
- Delete: Records are removed from database

## Module Responsibilities

### `src/logger.py`
- Configures logging system
- Sets up file and console handlers
- Manages log rotation

### `src/schema_detector.py`
- Reads Excel files
- Infers column data types
- Detects or generates primary keys
- Handles missing headers
- Cleans column names for SQL compatibility

### `src/db_manager.py`
- Manages SQLite database connections
- Creates tables from schemas
- Performs CRUD operations
- Handles transactions and errors

### `src/crud_generator.py`
- Generates Streamlit UI components
- Creates dynamic forms based on schema
- Handles user input validation
- Manages session state

### `app.py`
- Main application entry point
- Handles file upload and validation
- Orchestrates schema detection and database creation
- Integrates all modules

## Database Schema

### Table Structure
- Table name: `data` (configurable)
- Columns: Dynamically created from Excel schema
- Primary Key: Detected unique column or auto-generated `id`

### Type Mapping
- Python `int` → SQLite `INTEGER`
- Python `float` → SQLite `REAL`
- Python `str` → SQLite `TEXT`
- Python `date` → SQLite `TEXT` (ISO format)

## Error Handling

### Schema Detection Errors
- Empty files → `SchemaDetectionError`
- Corrupted files → `SchemaDetectionError`
- Missing data → `SchemaDetectionError`

### Database Errors
- Connection failures → `DatabaseError`
- SQL errors → `DatabaseError`
- Transaction rollbacks on errors

### User Interface Errors
- Validation errors shown to user
- Database errors logged
- Graceful error recovery

## Logging

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (fallbacks, data quality)
- **ERROR**: Error messages (failures, exceptions)
- **CRITICAL**: Critical errors (app crashes)

### Log Outputs
- **File**: `logs/app.log` (rotating, max 10MB, 5 backups)
- **Console**: INFO level and above

## Extension Points for Phase 2

### Multi-Sheet Support
- Extend `schema_detector.py` to process all sheets
- Modify `db_manager.py` to handle multiple tables
- Update `crud_generator.py` to show tabs per sheet

### Excel Feature Detection
- Add `excel_analyzer.py` module
- Detect data validation rules
- Identify formulas
- Extract chart information

### Enhanced Database
- Add PostgreSQL support
- Implement relationships between tables
- Add foreign key constraints

### Advanced UI
- Validation-aware forms
- Computed/read-only fields
- Chart visualizations
- Multi-table dashboards

## Performance Considerations

### Current Limitations (MVP)
- Single-threaded processing
- In-memory DataFrame operations
- SQLite for single-user scenarios
- 10,000 row limit for performance

### Future Optimizations
- Batch processing for large files
- Database connection pooling
- Caching for frequently accessed data
- Async operations for better responsiveness

## Security Considerations

### Current MVP
- Local file processing only
- No authentication required
- SQLite database (local)
- No data encryption

### Future Enhancements
- User authentication
- File upload validation
- SQL injection prevention (already handled via parameterized queries)
- Data encryption at rest
