# Excel to Streamlit MVP

A minimal viable product that converts Excel files into interactive Streamlit web applications with full CRUD (Create, Read, Update, Delete) functionality.

## Overview

This application allows you to upload an Excel file (`.xlsx` or `.xls`), automatically detects the schema, stores the data in SQLite, and generates a complete CRUD interface for managing your data through a web browser.

## Features

- **Excel File Upload**: Supports `.xlsx` and `.xls` formats
- **Automatic Schema Detection**: Infers column types (int, float, str, date) and primary keys
- **SQLite Storage**: Stores data in a local SQLite database
- **CRUD Interface**: Full Create, Read, Update, Delete operations
- **Simple UI**: Clean, tabbed interface for viewing and managing data

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd excel-to-streamlit
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Usage

1. **Upload Excel File**: Click "Choose an Excel file" and select your `.xlsx` or `.xls` file
   - Only the first sheet will be processed
   - Maximum file size: 50MB
   - Maximum rows: 10,000

2. **View Data**: Once uploaded, navigate to the "View" tab to see all records in a table

3. **Create Records**: Go to the "Create" tab to add new records using the generated form

4. **Edit Records**: Use the "Edit" tab to modify existing records

5. **Delete Records**: Use the "Delete" tab to remove records

## Project Structure

```
excel-to-streamlit/
├── app.py                 # Main Streamlit application
├── src/                   # Source code modules
│   ├── logger.py          # Logging configuration
│   ├── schema_detector.py # Excel schema detection
│   ├── db_manager.py      # SQLite database operations
│   └── crud_generator.py  # Streamlit UI generation
├── tests/                 # Unit tests
│   ├── fixtures/          # Test Excel files
│   └── test_*.py          # Test files
├── logs/                  # Application logs
├── docs/                  # Documentation
├── requirements.txt       # Production dependencies
└── requirements-dev.txt   # Development dependencies
```

## Testing

### Run Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_schema_detector.py
```

### Test Coverage

The project aims for >80% code coverage. View the HTML coverage report:
```bash
# After running pytest with coverage
open htmlcov/index.html
```

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for:
- Development setup
- Code style guidelines
- Testing guidelines
- Logging guidelines

## Documentation

- [API Documentation](docs/API.md) - Function and class reference
- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [Development Guide](docs/DEVELOPMENT.md) - Development guidelines

## Limitations (MVP)

- Only processes the first sheet of Excel files
- Maximum 10,000 rows per file
- Maximum 50MB file size
- No data validation rules from Excel
- No formula detection
- No chart generation
- Single table support only

## Future Enhancements (Phase 2)

- Multi-sheet support
- Excel data validation rules
- Formula detection and computed fields
- Chart generation
- PostgreSQL support
- Multiple Excel files
- Relationships between tables

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]
