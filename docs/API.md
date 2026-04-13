# API Documentation

Complete API reference for the Meeting Scheduling Service.

**Base URL:** `http://localhost:8000`

**Documentation:** `http://localhost:8000/docs` (OpenAPI/Swagger)

---

## Table of Contents

- [Health Check](#health-check)
- [Employee Endpoints](#employee-endpoints)
- [Room Endpoints](#room-endpoints)
- [Meeting Endpoints](#meeting-endpoints)
- [Available Slots Endpoint](#available-slots-endpoint)
- [Error Responses](#error-responses)

---

## Health Check

### GET /health

Check if the API and database are operational.

**Response:**
```json
{
  "status": "up"  // or "down" if database is unreachable
}
```

**Status Codes:**
- `200 OK` - Always returns 200, check status field

---

## Employee Endpoints

### GET /employees

Get all employees.

**Response:**
```json
[
  {
    "employee_id": 101,
    "full_name": "Alice Johnson"
  },
  {
    "employee_id": 102,
    "full_name": "Jack Smith"
  }
]
```

**Status Codes:**
- `200 OK` - Successfully retrieved employees

---

### GET /employees/{employee_id}

Get a specific employee by ID.

**Parameters:**
- `employee_id` (path, integer) - Employee ID

**Response:**
```json
{
  "employee_id": 101,
  "full_name": "Alice Johnson"
}
```

**Status Codes:**
- `200 OK` - Employee found
- `404 Not Found` - Employee doesn't exist

**Error Response:**
```json
{
  "detail": "Employee not found"
}
```

---

### POST /employees

Create a new employee.

**Request Body:**
```json
{
  "employee_id": 105,
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "employee_id": 105,
  "full_name": "John Doe"
}
```

**Status Codes:**
- `200 OK` - Employee created successfully
- `400 Bad Request` - Employee ID already exists

**Error Response:**
```json
{
  "detail": "Employee with id 105 already exists"
}
```

---

## Room Endpoints

### GET /rooms

Get all rooms.

**Response:**
```json
[
  {
    "room_id": 1,
    "room_name": "Negev Boardroom",
    "max_capacity": 20
  },
  {
    "room_id": 2,
    "room_name": "Galilee Hub",
    "max_capacity": 5
  }
]
```

**Status Codes:**
- `200 OK` - Successfully retrieved rooms

---

### GET /rooms/{room_id}

Get a specific room by ID.

**Parameters:**
- `room_id` (path, integer) - Room ID

**Response:**
```json
{
  "room_id": 1,
  "room_name": "Negev Boardroom",
  "max_capacity": 20
}
```

**Status Codes:**
- `200 OK` - Room found
- `404 Not Found` - Room doesn't exist

**Error Response:**
```json
{
  "detail": "Room not found"
}
```

---

### POST /rooms

Create a new room.

**Request Body:**
```json
{
  "room_id": 6,
  "room_name": "Conference Room A",
  "max_capacity": 15
}
```

**Response:**
```json
{
  "room_id": 6,
  "room_name": "Conference Room A",
  "max_capacity": 15
}
```

**Status Codes:**
- `200 OK` - Room created successfully
- `400 Bad Request` - Room ID already exists

**Error Response:**
```json
{
  "detail": "Room with id 6 already exists"
}
```

---

## Meeting Endpoints

### POST /meetings

Schedule a new meeting with automatic validation and conflict detection.

**Request Body:**
```json
{
  "room_id": 2,
  "start_time": "14:00",
  "end_time": "15:00",
  "employee_ids": [101, 102]
}
```

**Field Descriptions:**
- `room_id` (integer, required) - ID of the room to book
- `start_time` (time string, required) - Meeting start time in HH:MM format
- `end_time` (time string, required) - Meeting end time in HH:MM format
- `employee_ids` (array of integers, required) - List of employee IDs attending

**Response:**
```json
{
  "meeting_id": 7,
  "room_id": 2,
  "room_name": "Galilee Hub",
  "start_time": "14:00:00",
  "end_time": "15:00:00",
  "employees": [
    {
      "employee_id": 101,
      "full_name": "Alice Johnson"
    },
    {
      "employee_id": 102,
      "full_name": "Jack Smith"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Meeting scheduled successfully
- `400 Bad Request` - Validation error (see error types below)

**Validation Errors:**

1. **Room doesn't exist:**
```json
{"detail": "Room with id 999 does not exist"}
```

2. **Employee doesn't exist:**
```json
{"detail": "Employee with id 999 does not exist"}
```

3. **Room capacity exceeded:**
```json
{"detail": "Room 'Aravaland' has capacity 2 but 3 employees were assigned"}
```

4. **Before operating hours:**
```json
{"detail": "Meeting cannot start before 07:00"}
```

5. **After operating hours:**
```json
{"detail": "Meeting cannot end after 19:00"}
```

6. **Invalid time order:**
```json
{"detail": "Meeting start time must be before end time"}
```

7. **Room conflict:**
```json
{"detail": "Room 'Negev Boardroom' is already booked from 08:00 to 09:30"}
```

8. **Employee conflict:**
```json
{"detail": "Employee 'Alice Johnson' is already in a meeting from 15:00 to 16:00"}
```

---

## Available Slots Endpoint

### POST /meetings/available-slots

Find all available time slots for a group of employees with a specific duration.

**Request Body:**
```json
{
  "employee_ids": [101, 102],
  "duration_minutes": 60
}
```

**Field Descriptions:**
- `employee_ids` (array of integers, required) - List of employee IDs who need to attend
- `duration_minutes` (integer, required) - Meeting duration in minutes (1-720)

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
        },
        {
          "room_id": 4,
          "room_name": "Hermon Room",
          "max_capacity": 10
        }
      ]
    },
    {
      "start_time": "12:30:00",
      "end_time": "13:30:00",
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

**Algorithm:**
- Generates slots every 30 minutes from 07:00 to 19:00
- Only returns slots where ALL employees are available
- Only includes rooms with sufficient capacity and no conflicts
- Uses interval merging for efficient conflict detection

**Status Codes:**
- `200 OK` - Successfully found available slots
- `400 Bad Request` - Validation error

**Validation Errors:**

1. **Employee doesn't exist:**
```json
{"detail": "Employee with id 999 does not exist"}
```

2. **Negative duration:**
```json
{"detail": "Duration must be positive"}
```

3. **Duration too long:**
```json
{"detail": "Duration cannot exceed 12 hours"}
```

4. **No suitable rooms:**
```json
{"detail": "No rooms available with capacity for 25 employees. Maximum room capacity is 20"}
```

---

### POST /meetings/auto-schedule

Automatically schedules a meeting by finding and booking the best available slot.

**Request Body:**
```json
{
  "employee_ids": [101, 102, 103, 104],
  "duration_minutes": 60
}
```

**Field Descriptions:**
- `employee_ids` (array of integers, required) - List of employee IDs who need to attend
- `duration_minutes` (integer, required) - Meeting duration in minutes (1-720)

**Response:**
```json
{
  "meeting_id": 8,
  "room_id": 4,
  "room_name": "Hermon Room",
  "start_time": "09:30:00",
  "end_time": "10:30:00",
  "employees": [
    {"employee_id": 101, "full_name": "Alice Johnson"},
    {"employee_id": 102, "full_name": "Jack Smith"},
    {"employee_id": 103, "full_name": "Bob Miller"},
    {"employee_id": 104, "full_name": "Dana Cohen"}
  ]
}
```

**Selection Criteria:**
1. **Best Room Match** - Selects room with capacity closest to number of employees (minimizes waste)
2. **Earliest Time** - Books the first available slot with best matching room

**Examples:**
- 2 employees → Prefers room with capacity 2 over capacity 20
- 4 employees → Prefers room with capacity 5 over capacity 20

**Status Codes:**
- `200 OK` - Meeting successfully scheduled
- `400 Bad Request` - Validation error or no slots available

**Validation Errors:**

1. **No available slots:**
```json
{"detail": "No available slots found for the requested employees and duration"}
```

2. **Employee doesn't exist:**
```json
{"detail": "Employee with id 999 does not exist"}
```

3. **Invalid duration:**
```json
{"detail": "Duration must be positive"}
{"detail": "Duration cannot exceed 12 hours"}
```

4. **No suitable rooms:**
```json
{"detail": "No rooms available with capacity for 25 employees. Maximum room capacity is 20"}
```

**See also:** `docs/AUTO_SCHEDULE.md` for detailed examples and use cases

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message explaining what went wrong"
}
```

**Common HTTP Status Codes:**
- `200 OK` - Request successful
- `400 Bad Request` - Validation error or business logic violation
- `404 Not Found` - Resource doesn't exist
- `422 Unprocessable Entity` - Invalid request body format

---

## Data Types

### Time Format

Times use 24-hour format: `HH:MM` or `HH:MM:SS`

**Examples:**
- `"07:00"` - 7:00 AM
- `"14:30"` - 2:30 PM
- `"19:00"` - 7:00 PM

**Valid Range:**
- Start: `07:00` (earliest)
- End: `19:00` (latest)

### Employee Object

```json
{
  "employee_id": 101,
  "full_name": "Alice Johnson"
}
```

### Room Object

```json
{
  "room_id": 1,
  "room_name": "Negev Boardroom",
  "max_capacity": 20
}
```

### Meeting Object

```json
{
  "meeting_id": 7,
  "room_id": 2,
  "room_name": "Galilee Hub",
  "start_time": "14:00:00",
  "end_time": "15:00:00",
  "employees": [...]
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing rate limiting in production.

---

## Authentication

Currently no authentication is required. All endpoints are publicly accessible. Consider implementing authentication in production.

---

## Webhooks

Not currently supported.

---

## Versioning

Current version: v1 (implicit)

API versioning not yet implemented. Breaking changes will be documented in release notes.
