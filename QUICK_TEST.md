# Quick Testing Guide

## Step 1: Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (includes pytest)
pip install -r requirements-dev.txt
```

## Step 2: Run Unit Tests

```bash
# Run all tests
pytest

# Run with detailed output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

## Step 3: Test the Application Manually

```bash
# Start the Streamlit app
streamlit run app.py
```

Then in the browser:
1. Upload `tests/fixtures/sample_data.xlsx`
2. Check the "View" tab shows the data
3. Try creating a new record in "Create" tab
4. Try editing a record in "Edit" tab
5. Try deleting a record in "Delete" tab

## Quick Test Commands

```bash
# Test just schema detection
pytest tests/test_schema_detector.py -v

# Test just database operations
pytest tests/test_db_manager.py -v

# Test with coverage and see HTML report
pytest --cov=src --cov-report=html
start htmlcov/index.html  # Opens coverage report
```

## Verify Everything Works

```bash
# 1. Check imports work
python -c "from src.schema_detector import detect_schema; print('✓ Imports OK')"

# 2. Check test fixtures exist
python -c "from pathlib import Path; assert (Path('tests/fixtures/sample_data.xlsx').exists()); print('✓ Fixtures OK')"

# 3. Run a quick test
pytest tests/test_schema_detector.py::TestSchemaDetection::test_detect_schema_basic -v
```
