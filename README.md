# Meeting Scheduling Service

A FastAPI-based meeting room scheduling service with PostgreSQL database. Schedule meetings, allocate rooms, and find available time slots with automatic conflict detection.

## Features

- ✅ **Employee Management** - Add and manage employees
- ✅ **Room Management** - Add and manage meeting rooms with capacity
- ✅ **Meeting Scheduling** - Schedule meetings with automatic validation
- ✅ **Conflict Detection** - Prevents double-booking of rooms and employees
- ✅ **Available Slots** - Find available time slots for groups of employees
- ✅ **Auto-Schedule** - Automatically books the best available slot (NEW!)
- ✅ **Operating Hours** - Enforces 07:00-19:00 business hours
- ✅ **Interval Merging** - Efficient overlap detection algorithm

## Architecture

### Database Schema

```
employees
├── employee_id (PK)
└── full_name

rooms
├── room_id (PK)
├── room_name (unique)
└── max_capacity

meetings
├── meeting_id (PK, auto-increment)
├── room_id (FK → rooms)
├── start_time
└── end_time

employee_meetings (junction table)
├── employee_id (FK → employees)
└── meeting_id (FK → meetings)
```

### Tech Stack

- **Backend:** FastAPI (Python 3.14)
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Testing:** pytest
- **Container:** Docker

## Quick Start

### 1. Start PostgreSQL Database

```bash
docker-compose up -d
```

### 2. Create Tables and Load Initial Data

```bash
python scripts/create_meeting_tables.py
```

This creates all tables and loads initial data from CSV files:
- `resources/rooms.csv` - 5 meeting rooms
- `resources/meetings.csv` - 4 employees and 6 meetings

### 3. Start the API Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Access the API

- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## API Endpoints

### Health
- `GET /health` - Check database connectivity

### Employees
- `GET /employees` - List all employees
- `GET /employees/{employee_id}` - Get specific employee
- `POST /employees` - Add new employee

### Rooms
- `GET /rooms` - List all rooms
- `GET /rooms/{room_id}` - Get specific room
- `POST /rooms` - Add new room

### Meetings
- `POST /meetings` - Schedule a new meeting
- `POST /meetings/available-slots` - Find available time slots
- `POST /meetings/auto-schedule` - Automatically book best available slot (NEW!)

## Usage Examples

### Schedule a Meeting

```bash
POST http://localhost:8000/meetings
Content-Type: application/json

{
  "room_id": 2,
  "start_time": "14:00",
  "end_time": "15:00",
  "employee_ids": [101, 102]
}
```

**Response:**
```json
{
  "meeting_id": 7,
  "room_id": 2,
  "room_name": "Galilee Hub",
  "start_time": "14:00:00",
  "end_time": "15:00:00",
  "employees": [
    {"employee_id": 101, "full_name": "Alice Johnson"},
    {"employee_id": 102, "full_name": "Jack Smith"}
  ]
}
```

### Auto-Schedule a Meeting (NEW!)

Let the system automatically find and book the best available slot:

```bash
POST http://localhost:8000/meetings/auto-schedule
Content-Type: application/json

{
  "employee_ids": [101, 102],
  "duration_minutes": 60
}
```

**What it does:**
- Finds all available slots for the employees
- Selects room with capacity closest to employee count (minimizes waste)
- Books the earliest available slot
- Returns the created meeting

**Response:**
```json
{
  "meeting_id": 8,
  "room_id": 3,
  "room_name": "Aravaland",
  "start_time": "11:00:00",
  "end_time": "12:00:00",
  "employees": [
    {"employee_id": 101, "full_name": "Alice Johnson"},
    {"employee_id": 102, "full_name": "Jack Smith"}
  ]
}
```

---

### Find Available Slots

```bash
POST http://localhost:8000/meetings/available-slots
Content-Type: application/json

{
  "employee_ids": [101, 102],
  "duration_minutes": 60
}
```

**Response:**
```json
{
  "employee_ids": [101, 102],
  "duration_minutes": 60,
  "available_slots": [
    {
      "start_time": "11:00:00",
      "end_time": "12:00:00",
      "available_rooms": [
        {
          "room_id": 1,
          "room_name": "Negev Boardroom",
          "max_capacity": 20
        }
      ]
    }
  ]
}
```

## Validation Rules

### Meeting Creation Validates:

1. ✅ Room exists and has sufficient capacity
2. ✅ All employees exist
3. ✅ Time is within 07:00-19:00
4. ✅ Start time is before end time
5. ✅ Room is not double-booked (no overlapping meetings)
6. ✅ Employees are not in conflicting meetings

### Error Examples:

```json
// Room capacity exceeded
{"detail": "Room 'Aravaland' has capacity 2 but 3 employees were assigned"}

// Room conflict
{"detail": "Room 'Negev Boardroom' is already booked from 08:00 to 09:30"}

// Employee conflict
{"detail": "Employee 'Alice Johnson' is already in a meeting from 15:00 to 16:00"}

// Outside hours
{"detail": "Meeting cannot start before 07:00"}
```

## Testing

### Quick Start

```bash
# Setup test database (first time)
python tests/setup_test_db.py

# Run all tests
python tests/run_tests.py
```

### Test Suite

- **109 Total Tests** ✅
  - 60 Unit tests (CRUD operations)
  - 45 Integration tests (API endpoints)
  - 4 Other tests

### Test Database

⚠️ **Important**: Tests use a separate database (`interview_db_test`) to protect production data.

```
PostgreSQL Container
├── interview_db       (Production - Safe)
└── interview_db_test  (Tests - Isolated)
```

### Run Specific Tests

```bash
# All tests with cleanup
python tests/run_tests.py

# Unit tests only
pytest tests/test_crud.py -v

# Integration tests only
pytest tests/test_integration.py -v

# Specific test
pytest tests/test_crud.py::test_create_meeting_success -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

📖 **Full docs**: See [docs/](docs/) folder (3 files)

## Project Structure

```
schedule-a-meeting-task/
├── app/
│   ├── crud/            # Business logic (modular)
│   │   ├── items.py
│   │   ├── employees.py
│   │   ├── rooms.py
│   │   └── meetings.py
│   ├── routes/          # API endpoints (modular)
│   │   ├── items.py
│   │   ├── employees.py
│   │   ├── rooms.py
│   │   └── meetings.py
│   ├── main.py          # FastAPI app
│   ├── database.py      # DB connection
│   ├── schemas.py       # Validation
│   └── models.py        # ORM models
├── tests/               # 109 tests
├── docs/                # 3 doc files
│   ├── API.md
│   ├── SETUP.md
│   └── REFACTORING.md
├── scripts/             # Setup scripts
└── resources/           # CSV data
```

## Algorithm Details

### Interval Overlap Detection

Uses the efficient formula: `start1 < end2 AND start2 < end1`

This detects all overlap types:
- Partial overlap
- Complete containment
- Exact match
- Any intersection

### Available Slots Algorithm

1. Validate all employees exist
2. Collect busy intervals for all employees
3. **Merge overlapping intervals** (reduces O(n²) to O(n log n))
4. Filter rooms by capacity
5. Generate slots every 30 minutes (07:00-19:00)
6. For each slot:
   - Check if all employees are available (against merged intervals)
   - Find rooms without conflicts
7. Return slots with available rooms

## Database Configuration

Edit `app/database.py` to change database connection:

```python
DATABASE_URL = "postgresql://interview_user:interview_pass@localhost:5433/interview_db"
```

Docker container settings in `docker-compose.yml`:
- Port: 5433 (mapped from container 5432)
- Username: interview_user
- Password: interview_pass
- Database: interview_db

## Development

### Add New Employee

```bash
POST /employees
{
  "employee_id": 105,
  "full_name": "New Employee"
}
```

### Add New Room

```bash
POST /rooms
{
  "room_id": 6,
  "room_name": "Conference Room A",
  "max_capacity": 12
}
```

## Business Rules

1. **Single Day Only** - System schedules for one day only
2. **Operating Hours** - 07:00 to 19:00 only
3. **No Overlaps** - Rooms and employees cannot double-book
4. **Capacity Limits** - Meetings cannot exceed room capacity
5. **30-Minute Slots** - Available slots generated every 30 minutes

## Future Enhancements

- [ ] Multi-day scheduling
- [ ] Recurring meetings
- [ ] Meeting cancellation/modification
- [ ] Email notifications
- [ ] Calendar integration
- [ ] Room amenities filtering
- [ ] Employee availability preferences
- [ ] Meeting history and analytics

## License

MIT

## Documentation

| Document | Description |
|----------|-------------|
| [docs/SETUP.md](docs/SETUP.md) | Setup, testing & troubleshooting |
| [docs/API.md](docs/API.md) | Complete API reference |
| [docs/REFACTORING.md](docs/REFACTORING.md) | Code structure guide |
