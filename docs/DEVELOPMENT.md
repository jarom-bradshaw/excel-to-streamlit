# Development Guide

This guide provides information for developers working on the Excel to Streamlit MVP project.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (for version control)

### Initial Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd excel-to-streamlit
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Verify installation:
```bash
pytest --version
streamlit --version
```

## Code Style Guidelines

### Python Style

- Follow PEP 8 style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Code Formatting

We use `black` for automatic code formatting:

```bash
# Format all Python files
black src/ tests/ app.py

# Check formatting without making changes
black --check src/ tests/ app.py
```

### Linting

We use `flake8` for linting:

```bash
# Run linter
flake8 src/ tests/ app.py

# Common flake8 configuration is in setup.cfg or .flake8
```

### Type Hints

- Use type hints for all function parameters and return types
- Use `typing` module for complex types
- Example:
```python
from typing import Dict, List, Optional

def process_data(data: Dict[str, Any]) -> Optional[List[str]]:
    ...
```

## Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_schema_detector.py

# Run specific test
pytest tests/test_schema_detector.py::TestSchemaDetection::test_detect_schema_basic

# Run with coverage
pytest --cov=src --cov-report=html
```

### Writing Tests

1. **Test Structure**: One test file per module (`test_<module>.py`)
2. **Test Classes**: Group related tests in classes
3. **Test Names**: Use descriptive names starting with `test_`
4. **Fixtures**: Use pytest fixtures for common setup
5. **Assertions**: Use clear, descriptive assertions

**Example:**
```python
import pytest
from src.schema_detector import detect_schema

class TestSchemaDetection:
    def test_detect_schema_basic(self):
        """Test basic schema detection."""
        schema = detect_schema("test.xlsx")
        assert "columns" in schema
        assert len(schema["columns"]) > 0
```

### Test Coverage

- Aim for >80% code coverage
- Focus on testing business logic
- Test error cases and edge cases
- Use in-memory databases for database tests

### Test Fixtures

- Store test Excel files in `tests/fixtures/`
- Use descriptive names: `sample_data.xlsx`, `sample_no_headers.xlsx`
- Keep fixtures small and focused

## Logging Guidelines

### Using Loggers

Each module should have its own logger:

```python
from src.logger import get_logger

logger = get_logger(__name__)

def my_function():
    logger.info("Starting operation")
    try:
        # ... code ...
        logger.debug(f"Processed {count} items")
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
```

### Log Levels

- **DEBUG**: Detailed diagnostic information (development only)
- **INFO**: General informational messages (normal operations)
- **WARNING**: Warning messages (fallbacks, data quality issues)
- **ERROR**: Error messages (failures, exceptions)
- **CRITICAL**: Critical errors (app crashes, data loss)

### Best Practices

- Log at appropriate levels
- Include context in log messages
- Use `exc_info=True` for exceptions
- Don't log sensitive information
- Use structured logging when possible

## Error Handling

### Custom Exceptions

Create custom exceptions for domain-specific errors:

```python
class SchemaDetectionError(Exception):
    """Custom exception for schema detection errors."""
    pass
```

### Error Handling Pattern

```python
try:
    # Operation
    result = perform_operation()
    logger.info(f"Operation successful: {result}")
    return result
except SpecificError as e:
    logger.error(f"Specific error occurred: {e}", exc_info=True)
    raise CustomError(f"User-friendly message: {e}")
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    raise
```

## Documentation

### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def process_data(data: Dict[str, Any]) -> Optional[List[str]]:
    """
    Process data and return results.

    Args:
        data: Dictionary containing input data.

    Returns:
        List of processed strings, or None if processing fails.

    Raises:
        ValueError: If data is invalid.
    """
    ...
```

### Inline Comments

- Explain "why", not "what"
- Keep comments up-to-date
- Remove commented-out code

## Git Workflow

### Branching

- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: Feature branches
- `fix/*`: Bug fix branches

### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add multi-sheet support
fix: Handle empty Excel files correctly
docs: Update API documentation
test: Add tests for schema detection
```

### Pre-commit Checks

Before committing:
1. Run tests: `pytest`
2. Format code: `black src/ tests/ app.py`
3. Check linting: `flake8 src/ tests/ app.py`
4. Verify no debug code or print statements

## Debugging

### Using Logs

Check `logs/app.log` for detailed application logs:

```bash
# View recent logs
tail -f logs/app.log

# Search logs
grep "ERROR" logs/app.log
```

### Debug Mode

Enable debug logging:

```python
from src.logger import setup_logging
setup_logging("DEBUG")
```

### Streamlit Debugging

- Use `st.write()` for quick debugging (remove before commit)
- Check Streamlit's built-in error messages
- Use browser developer tools for UI issues

## Performance

### Profiling

Use Python profilers to identify bottlenecks:

```bash
# Using cProfile
python -m cProfile -o profile.stats app.py

# Using line_profiler
kernprof -l -v app.py
```

### Optimization Tips

- Use pandas vectorized operations
- Minimize database queries
- Cache expensive computations
- Use generators for large datasets

## Common Tasks

### Adding a New Module

1. Create module in `src/`
2. Add logger: `logger = get_logger(__name__)`
3. Add docstrings and type hints
4. Write tests in `tests/test_<module>.py`
5. Update documentation

### Adding a New Dependency

1. Add to `requirements.txt` or `requirements-dev.txt`
2. Update version pinning if needed
3. Document in README if user-facing
4. Test installation in clean environment

### Updating Documentation

1. Update relevant doc files in `docs/`
2. Update README.md if user-facing changes
3. Update API.md for API changes
4. Keep examples up-to-date

## Troubleshooting

### Common Issues

**Import Errors:**
- Ensure virtual environment is activated
- Check Python path
- Verify all dependencies are installed

**Database Errors:**
- Check file permissions
- Verify database file isn't locked
- Check SQL syntax

**Streamlit Issues:**
- Clear Streamlit cache: `streamlit cache clear`
- Restart Streamlit server
- Check browser console for errors

### Getting Help

- Check logs in `logs/app.log`
- Review test cases for usage examples
- Check documentation in `docs/`
- Search existing issues

## Contributing

### Before Submitting

1. ✅ All tests pass
2. ✅ Code is formatted with black
3. ✅ No linting errors
4. ✅ Documentation is updated
5. ✅ Logging is appropriate
6. ✅ Error handling is in place

### Code Review Checklist

- Code follows style guidelines
- Tests are comprehensive
- Documentation is clear
- Error handling is appropriate
- Logging is used correctly
- No security issues
