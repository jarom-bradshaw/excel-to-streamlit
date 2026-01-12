# Testing Guide

This guide explains how to test the Excel to Streamlit MVP application.

## Prerequisites

Make sure you have installed all dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Running Unit Tests

### Run All Tests

```bash
pytest
```

This will:
- Run all tests in the `tests/` directory
- Show verbose output (`-v`)
- Generate coverage reports
- Display coverage summary in terminal

### Run Tests with Coverage Report

```bash
pytest --cov=src --cov-report=html
```

This generates:
- Terminal coverage summary
- HTML report in `htmlcov/index.html` (open in browser)
- XML report for CI/CD tools

### Run Specific Test Files

```bash
# Test schema detector only
pytest tests/test_schema_detector.py

# Test database manager only
pytest tests/test_db_manager.py

# Test CRUD generator only
pytest tests/test_crud_generator.py

# Test main app only
pytest tests/test_app.py
```

### Run Specific Test Functions

```bash
# Run a specific test
pytest tests/test_schema_detector.py::TestSchemaDetection::test_detect_schema_basic

# Run all tests in a class
pytest tests/test_schema_detector.py::TestSchemaDetection
```

### Verbose Output

```bash
# More detailed output
pytest -v

# Even more verbose (shows print statements)
pytest -vv -s
```

## Manual Testing

### 1. Start the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 2. Test File Upload

1. **Valid Excel File**:
   - Use `tests/fixtures/sample_data.xlsx`
   - Should successfully upload and process
   - Should show success message with record count

2. **Invalid File Types**:
   - Try uploading a `.pdf` or `.txt` file
   - Should show error: "Unsupported file format"

3. **Large File** (if you have one > 50MB):
   - Should show error: "File exceeds 50MB limit"

### 3. Test CRUD Operations

**View Tab:**
- Should display all records in a table
- Check that all columns are visible
- Verify data matches Excel file

**Create Tab:**
- Fill out the form with new data
- Click "Create Record"
- Should show success message
- New record should appear in View tab

**Edit Tab:**
- Select a record from dropdown
- Modify some fields
- Click "Update Record"
- Should show success message
- Changes should appear in View tab

**Delete Tab:**
- Select a record from dropdown
- Click "Delete Record"
- Should show success message
- Record should disappear from View tab

### 4. Test Edge Cases

**Missing Headers:**
- Use `tests/fixtures/sample_no_headers.xlsx`
- Should auto-generate column names (Column1, Column2, etc.)

**No Primary Key:**
- Use `tests/fixtures/sample_no_pk.xlsx`
- Should auto-generate `id` column

**Empty File:**
- Use `tests/fixtures/sample_empty.xlsx`
- Should show error: "No data found in first sheet"

## Checking Test Coverage

After running tests with coverage:

```bash
# View HTML coverage report
# On Windows:
start htmlcov/index.html

# On Mac/Linux:
open htmlcov/index.html
```

The report shows:
- Which lines are covered
- Which lines are missing
- Overall coverage percentage

**Target**: >80% code coverage

## Testing Individual Modules

### Test Schema Detector

```bash
# Run schema detector tests
pytest tests/test_schema_detector.py -v

# Test with your own Excel file
python -c "from src.schema_detector import detect_schema; print(detect_schema('your_file.xlsx'))"
```

### Test Database Manager

```bash
# Run database manager tests
pytest tests/test_db_manager.py -v

# Test database operations manually
python -c "
from src.db_manager import DatabaseManager
db = DatabaseManager(db_path=':memory:', table_name='test')
schema = {'columns': ['id', 'name'], 'types': {'id': 'int', 'name': 'str'}, 'primary_key': 'id'}
db.create_table(schema)
print('Table created successfully')
"
```

## Debugging Tests

### Run Tests with Debug Output

```bash
# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb
```

### Check Logs

Test logs are written to `logs/app.log`:

```bash
# View recent logs
tail -f logs/app.log

# On Windows PowerShell:
Get-Content logs/app.log -Tail 50

# Search for errors
grep ERROR logs/app.log
```

## Continuous Integration Testing

For CI/CD pipelines, use:

```bash
# Run tests with XML coverage report
pytest --cov=src --cov-report=xml --junitxml=test-results.xml
```

## Common Test Issues

### Import Errors

If you see import errors:
```bash
# Make sure you're in the project root directory
cd excel-to-streamlit

# Verify Python path
python -c "import sys; print(sys.path)"

# Install in development mode (if needed)
pip install -e .
```

### Database Locked Errors

If SQLite database is locked:
- Close any open database connections
- Delete `data.db` file
- Restart tests

### Missing Test Fixtures

If fixtures are missing:
```bash
# Recreate fixtures
python tests/create_fixtures.py
```

## Quick Test Checklist

- [ ] All unit tests pass: `pytest`
- [ ] Coverage > 80%: `pytest --cov=src`
- [ ] App starts: `streamlit run app.py`
- [ ] Can upload Excel file
- [ ] Can view data
- [ ] Can create record
- [ ] Can edit record
- [ ] Can delete record
- [ ] Error handling works (invalid files, empty files)
- [ ] Logs are generated in `logs/app.log`

## Performance Testing

For large files (approaching 10,000 row limit):

```bash
# Create a large test file
python -c "
import pandas as pd
df = pd.DataFrame({'id': range(10000), 'name': ['Test'] * 10000})
df.to_excel('large_test.xlsx', index=False)
print('Created large test file')
"

# Test upload in Streamlit app
# Should process successfully
```

## Next Steps

After testing:
1. Review test coverage report
2. Add tests for any missing coverage
3. Fix any failing tests
4. Update documentation if needed
