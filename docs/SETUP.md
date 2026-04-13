# Setup & Testing

Quick guide to get started and run tests.

## Quick Start

### 1. Start Database
```bash
docker-compose up -d
```

### 2. Create Tables
```bash
python scripts/create_meeting_tables.py
```

### 3. Run Server
```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Access API
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

---

## Running Tests

### Setup Test Database (First Time)
```bash
python tests/setup_test_db.py
```

### Run All Tests (109 tests)
```bash
python tests/run_tests.py
```

### Run Specific Test Categories
```bash
pytest tests/test_crud.py -v          # 60 unit tests
pytest tests/test_integration.py -v   # 45 integration tests
pytest tests/test_api.py -v           # 4 API tests
```

### Test Database
- Tests use separate database: `interview_db_test`
- Production database (`interview_db`) is never touched
- Tests clean up automatically after running

---

## Troubleshooting

### Database Won't Start
```bash
docker ps                    # Check if running
docker-compose logs          # View logs
docker-compose restart       # Restart
```

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

### Tests Failing
```bash
# Recreate test database
python tests/setup_test_db.py
```

### Connection Error
Check `app/database.py` connection string:
```python
DATABASE_URL = "postgresql://interview_user:interview_pass@localhost:5433/interview_db"
```

---

## Database Configuration

**Docker Settings** (`docker-compose.yml`):
- Port: 5433
- Username: interview_user
- Password: interview_pass
- Database: interview_db

**Connect with psql**:
```bash
psql -h localhost -p 5433 -U interview_user -d interview_db
```
