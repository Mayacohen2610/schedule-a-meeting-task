# Meeting Scheduling Service

FastAPI + PostgreSQL service for scheduling meetings, checking availability, and auto-booking the best slot without room/employee conflicts.

## ✨ Features

- 👥 **Employee management**
  - Create and view employees who can participate in meetings.
  - Employee IDs are explicit, which makes test data and integrations predictable.

- 🏢 **Room management**
  - Create and view meeting rooms with a maximum capacity.
  - Capacity is enforced during scheduling to prevent overbooking.

- 📅 **Meeting scheduling with validation**
  - Schedule a meeting in a specific room and time window.
  - The API validates room existence, attendee existence, time range, and capacity.

- 🚫 **Conflict detection**
  - Prevents double-booking of rooms.
  - Prevents assigning employees to overlapping meetings.
  - Uses interval overlap logic for reliable conflict checks.

- 🔎 **Available slots search**
  - Finds all valid time windows for a group of employees and meeting duration.
  - Returns only slots where all attendees are free and at least one room can host them.
  - Provides the list of available rooms per slot.

- 🤖 **Auto-scheduling**
  - Finds valid slots and books one automatically.
  - Chooses the room with capacity closest to attendee count (to reduce wasted space).
  - Selects the earliest valid slot for quick booking.

- 🕒 **Business-hour enforcement**
  - Scheduling is limited to `07:00`-`19:00`.
  - Slot generation advances in 30-minute increments.

## 🚀 Quick Start

1) Start PostgreSQL:
```bash
docker-compose up -d
```

2) Create tables and seed initial data:
```bash
python scripts/create_meeting_tables.py
```

3) Run the API:
```bash
uvicorn app.main:app --reload --port 8000
```

4) Open:
- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## 🌐 API Overview

Base URL: `http://localhost:8000`

### Health
- `GET /health` - API + DB status (`{"status":"up"|"down"}`)

### Employees
- `GET /employees` - list employees
- `GET /employees/{employee_id}` - get one employee
- `POST /employees` - create employee

### Rooms
- `GET /rooms` - list rooms
- `GET /rooms/{room_id}` - get one room
- `POST /rooms` - create room

### Meetings
- `POST /meetings` - schedule a specific room/time
- `POST /meetings/available-slots` - return valid time windows + rooms
- `POST /meetings/auto-schedule` - auto-book earliest valid option

### Example: Create Meeting

```json
POST /meetings
{
  "room_id": 2,
  "start_time": "14:00",
  "end_time": "15:00",
  "employee_ids": [101, 102]
}
```

### Example: Find Slots

```json
POST /meetings/available-slots
{
  "employee_ids": [101, 102],
  "duration_minutes": 60
}
```

### Example: Auto-Schedule

```json
POST /meetings/auto-schedule
{
  "employee_ids": [101, 102],
  "duration_minutes": 60
}
```

### Example Error Response

```json
{"detail": "Room 'Aravaland' has capacity 2 but 3 employees were assigned"}
```

## ✅ Validation and Error Rules

- Error shape:
  ```json
  {"detail": "Human-readable message"}
  ```

- Common checks for `POST /meetings`:
  - Room exists
  - Employees exist
  - Room has enough capacity
  - `start_time < end_time`
  - Time range is within `07:00-19:00`
  - No room conflict with existing meetings
  - No employee conflict with existing meetings

- Common checks for slot search / auto-schedule:
  - Employees exist
  - `duration_minutes` is valid (`1-720`)
  - At least one room can fit the attendee count
  - At least one valid slot exists (for auto-schedule)

## 🧠 Scheduling Logic

### Overlap Rule

Two meetings overlap if:
`start1 < end2 AND start2 < end1`

This covers partial overlap, full containment, and exact overlap.

### Available Slots Algorithm
1. Validate employees and duration
2. Collect employee busy intervals
3. Merge overlaps for efficient checks
4. Generate candidate slots every 30 minutes
5. Keep slots where all employees are free
6. Keep rooms with enough capacity and no conflict

### Auto-Schedule Selection
1. Choose room with capacity closest to attendee count
2. Book the earliest matching slot

## 🏗️ Architecture

### Database Schema
- `employees(employee_id, full_name)`
- `rooms(room_id, room_name, max_capacity)`
- `meetings(meeting_id, room_id, start_time, end_time)`
- `employee_meetings(employee_id, meeting_id)`

### Project Structure
```text
app/
  crud/        # Business logic by entity
  routes/      # API routers by entity
  models.py    # SQLAlchemy models
  schemas.py   # Pydantic schemas
  database.py  # DB connection
  main.py      # FastAPI app
tests/
scripts/
resources/
```

The project was refactored from monolithic CRUD/routes files into modular entity-based files for easier maintenance and testing.

## 🧪 Testing

First-time test DB setup:
```bash
python tests/setup_test_db.py
```

Run all tests:
```bash
python tests/run_tests.py
```

Run by category:
```bash
pytest tests/test_crud.py -v
pytest tests/test_integration.py -v
pytest tests/test_api.py -v
```

Notes:
- Tests use isolated DB `interview_db_test`
- Production DB `interview_db` is not touched
- Tests currently include unit, integration, and endpoint coverage.

## ⚙️ Configuration

Default DB URL in `app/database.py`:

```python
DATABASE_URL = "postgresql://interview_user:interview_pass@localhost:5433/interview_db"
```

Docker DB defaults:
- Port: `5433`
- User: `interview_user`
- Password: `interview_pass`
- Database: `interview_db`

## 🛠️ Troubleshooting

Database issues:
```bash
docker ps
docker-compose logs
docker-compose restart
```

Port conflict:
```bash
uvicorn app.main:app --reload --port 8001
```

Test DB reset:
```bash
python tests/setup_test_db.py
```

## 📌 Business Rules (At a Glance)

1. Single-day scheduling scope
2. Operating hours are `07:00` to `19:00`
3. No room or employee double-booking
4. Room capacity must fit attendees
5. Slot search uses 30-minute steps
