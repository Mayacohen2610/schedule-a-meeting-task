# Tests Directory

Quick reference for running tests. For complete documentation, see [../docs/TESTING.md](../docs/TESTING.md).

## Quick Start

```bash
# Setup test database (first time only)
python tests/setup_test_db.py

# Run all tests
python tests/run_tests.py
```

## Test Files

- `conftest.py` - Test configuration and fixtures
- `setup_test_db.py` - Initialize test database schema
- `run_tests.py` - Test runner with automatic cleanup
- `test_crud.py` - 60 unit tests (CRUD operations)
- `test_integration.py` - 45 integration tests (API endpoints)
- `test_db_connection.py` - 3 database connectivity tests
- `test_api.py` - 4 basic API tests

## Test Database

⚠️ **Important**: Tests use a separate database (`interview_db_test`) to protect production data.

- **Production**: `interview_db` ← Safe from tests
- **Tests**: `interview_db_test` ← Isolated test environment

## Common Commands

```bash
# Run all tests
python tests/run_tests.py

# Run specific file
pytest tests/test_crud.py -v

# Run specific test
pytest tests/test_crud.py::test_create_meeting_success -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## Test Statistics

- **Total**: 109 tests
- **Unit**: 60 tests
- **Integration**: 45 tests
- **Other**: 4 tests

All tests passing ✅

## Documentation

📖 **Full documentation**: [../docs/TESTING.md](../docs/TESTING.md)
📖 **Test database setup**: [../docs/TEST_DATABASE.md](../docs/TEST_DATABASE.md)
