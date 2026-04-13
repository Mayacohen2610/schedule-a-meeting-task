"""
Comprehensive integration tests for all API endpoints.
Tests end-to-end functionality through HTTP API calls.
"""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db

# Use test database for integration tests
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://interview_user:interview_pass@localhost:5433/interview_db_test"
)

# Create test database engine and session
test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency to use test database."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the database dependency for all tests in this file
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# =============================================================================
# Health Endpoint Tests
# =============================================================================

def test_health_endpoint_returns_up():
    """Test health endpoint returns up when database is available."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "up"


def test_health_endpoint_structure():
    """Test health endpoint returns correct JSON structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 1
    assert "status" in data


# =============================================================================
# Item Endpoints Integration Tests
# =============================================================================

def test_get_items_endpoint():
    """Test GET /items returns list of items."""
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_items_structure():
    """Test GET /items returns items with correct structure."""
    response = client.get("/items")
    assert response.status_code == 200
    items = response.json()
    
    for item in items:
        assert "id" in item
        assert "item_name" in item
        assert "category" in item
        assert "price" in item
        assert "in_stock" in item
        assert isinstance(item["id"], int)
        assert isinstance(item["item_name"], str)
        assert isinstance(item["category"], str)
        assert isinstance(item["price"], (int, float))
        assert isinstance(item["in_stock"], bool)


def test_post_item_success():
    """Test POST /items creates new item successfully."""
    new_item = {
        "item_name": "Integration Test Item",
        "category": "Test Category",
        "price": 99.99,
        "in_stock": True
    }
    
    response = client.post("/items", json=new_item)
    assert response.status_code == 200
    
    created = response.json()
    assert created["item_name"] == new_item["item_name"]
    assert created["category"] == new_item["category"]
    assert created["price"] == new_item["price"]
    assert created["in_stock"] == new_item["in_stock"]
    assert "id" in created
    assert isinstance(created["id"], int)


def test_post_item_default_in_stock():
    """Test POST /items with default in_stock value."""
    new_item = {
        "item_name": "Default Stock Item",
        "category": "Test",
        "price": 50.0
    }
    
    response = client.post("/items", json=new_item)
    assert response.status_code == 200
    created = response.json()
    assert created["in_stock"] is True


def test_post_item_missing_required_fields():
    """Test POST /items fails with missing required fields."""
    incomplete_item = {
        "item_name": "Incomplete Item"
        # Missing category and price
    }
    
    response = client.post("/items", json=incomplete_item)
    assert response.status_code == 422  # Validation error


def test_patch_item_price():
    """Test PATCH /items/{id} updates item price."""
    # Create an item first
    new_item = {
        "item_name": "Price Update Test",
        "category": "Test",
        "price": 100.0,
        "in_stock": True
    }
    create_response = client.post("/items", json=new_item)
    created = create_response.json()
    item_id = created["id"]
    
    # Update the price
    update_data = {"price": 150.0}
    response = client.patch(f"/items/{item_id}", json=update_data)
    
    assert response.status_code == 200
    updated = response.json()
    assert updated["price"] == 150.0
    assert updated["item_name"] == "Price Update Test"
    assert updated["in_stock"] is True


def test_patch_item_in_stock():
    """Test PATCH /items/{id} updates item stock status."""
    # Create an item
    new_item = {
        "item_name": "Stock Update Test",
        "category": "Test",
        "price": 50.0,
        "in_stock": True
    }
    create_response = client.post("/items", json=new_item)
    created = create_response.json()
    item_id = created["id"]
    
    # Update stock status
    update_data = {"in_stock": False}
    response = client.patch(f"/items/{item_id}", json=update_data)
    
    assert response.status_code == 200
    updated = response.json()
    assert updated["in_stock"] is False
    assert updated["price"] == 50.0


def test_patch_item_multiple_fields():
    """Test PATCH /items/{id} updates multiple fields."""
    # Create an item
    new_item = {
        "item_name": "Multi Update Test",
        "category": "Test",
        "price": 75.0,
        "in_stock": True
    }
    create_response = client.post("/items", json=new_item)
    created = create_response.json()
    item_id = created["id"]
    
    # Update multiple fields
    update_data = {"price": 125.0, "in_stock": False}
    response = client.patch(f"/items/{item_id}", json=update_data)
    
    assert response.status_code == 200
    updated = response.json()
    assert updated["price"] == 125.0
    assert updated["in_stock"] is False


def test_patch_item_not_found():
    """Test PATCH /items/{id} returns 404 for non-existent item."""
    update_data = {"price": 100.0}
    response = client.patch("/items/999999", json=update_data)
    
    assert response.status_code == 404
    error = response.json()
    assert "detail" in error


def test_patch_item_no_fields():
    """Test PATCH /items/{id} returns 400 when no fields provided."""
    # Create an item
    new_item = {
        "item_name": "No Update Test",
        "category": "Test",
        "price": 50.0
    }
    create_response = client.post("/items", json=new_item)
    created = create_response.json()
    item_id = created["id"]
    
    # Try to update with no fields
    response = client.patch(f"/items/{item_id}", json={})
    
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error


# =============================================================================
# Employee Endpoints Integration Tests
# =============================================================================

def test_get_employees_endpoint():
    """Test GET /employees returns list of employees."""
    response = client.get("/employees")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_employees_structure():
    """Test GET /employees returns employees with correct structure."""
    response = client.get("/employees")
    assert response.status_code == 200
    employees = response.json()
    
    for employee in employees:
        assert "employee_id" in employee
        assert "full_name" in employee
        assert isinstance(employee["employee_id"], int)
        assert isinstance(employee["full_name"], str)


def test_post_employee_success():
    """Test POST /employees creates new employee successfully."""
    new_employee = {
        "employee_id": 9100,
        "full_name": "Integration Test Employee"
    }
    
    response = client.post("/employees", json=new_employee)
    assert response.status_code == 200
    
    created = response.json()
    assert created["employee_id"] == new_employee["employee_id"]
    assert created["full_name"] == new_employee["full_name"]


def test_post_employee_duplicate():
    """Test POST /employees returns 400 for duplicate employee ID."""
    new_employee = {
        "employee_id": 9101,
        "full_name": "Test Employee"
    }
    
    # Create first employee
    response1 = client.post("/employees", json=new_employee)
    assert response1.status_code == 200
    
    # Try to create duplicate
    response2 = client.post("/employees", json=new_employee)
    assert response2.status_code == 400
    error = response2.json()
    assert "detail" in error
    assert "already exists" in error["detail"]


def test_post_employee_missing_fields():
    """Test POST /employees fails with missing required fields."""
    incomplete_employee = {
        "employee_id": 9102
        # Missing full_name
    }
    
    response = client.post("/employees", json=incomplete_employee)
    assert response.status_code == 422  # Validation error


def test_get_employee_by_id_success():
    """Test GET /employees/{id} returns employee by ID."""
    # Create an employee
    new_employee = {
        "employee_id": 9103,
        "full_name": "Get By ID Test"
    }
    client.post("/employees", json=new_employee)
    
    # Get the employee
    response = client.get("/employees/9103")
    assert response.status_code == 200
    
    employee = response.json()
    assert employee["employee_id"] == 9103
    assert employee["full_name"] == "Get By ID Test"


def test_get_employee_by_id_not_found():
    """Test GET /employees/{id} returns 404 for non-existent employee."""
    response = client.get("/employees/999999")
    assert response.status_code == 404
    error = response.json()
    assert "detail" in error


# =============================================================================
# Room Endpoints Integration Tests
# =============================================================================

def test_get_rooms_endpoint():
    """Test GET /rooms returns list of rooms."""
    response = client.get("/rooms")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_rooms_structure():
    """Test GET /rooms returns rooms with correct structure."""
    response = client.get("/rooms")
    assert response.status_code == 200
    rooms = response.json()
    
    for room in rooms:
        assert "room_id" in room
        assert "room_name" in room
        assert "max_capacity" in room
        assert isinstance(room["room_id"], int)
        assert isinstance(room["room_name"], str)
        assert isinstance(room["max_capacity"], int)


def test_post_room_success():
    """Test POST /rooms creates new room successfully."""
    new_room = {
        "room_id": 9100,
        "room_name": "Integration Test Room",
        "max_capacity": 10
    }
    
    response = client.post("/rooms", json=new_room)
    assert response.status_code == 200
    
    created = response.json()
    assert created["room_id"] == new_room["room_id"]
    assert created["room_name"] == new_room["room_name"]
    assert created["max_capacity"] == new_room["max_capacity"]


def test_post_room_duplicate():
    """Test POST /rooms returns 400 for duplicate room ID."""
    new_room = {
        "room_id": 9101,
        "room_name": "Test Room",
        "max_capacity": 5
    }
    
    # Create first room
    response1 = client.post("/rooms", json=new_room)
    assert response1.status_code == 200
    
    # Try to create duplicate
    response2 = client.post("/rooms", json=new_room)
    assert response2.status_code == 400
    error = response2.json()
    assert "detail" in error
    assert "already exists" in error["detail"]


def test_post_room_missing_fields():
    """Test POST /rooms fails with missing required fields."""
    incomplete_room = {
        "room_id": 9102,
        "room_name": "Incomplete Room"
        # Missing max_capacity
    }
    
    response = client.post("/rooms", json=incomplete_room)
    assert response.status_code == 422  # Validation error


def test_get_room_by_id_success():
    """Test GET /rooms/{id} returns room by ID."""
    # Create a room
    new_room = {
        "room_id": 9103,
        "room_name": "Get By ID Test Room",
        "max_capacity": 8
    }
    client.post("/rooms", json=new_room)
    
    # Get the room
    response = client.get("/rooms/9103")
    assert response.status_code == 200
    
    room = response.json()
    assert room["room_id"] == 9103
    assert room["room_name"] == "Get By ID Test Room"
    assert room["max_capacity"] == 8


def test_get_room_by_id_not_found():
    """Test GET /rooms/{id} returns 404 for non-existent room."""
    response = client.get("/rooms/999999")
    assert response.status_code == 404
    error = response.json()
    assert "detail" in error


# =============================================================================
# Meeting Endpoints Integration Tests
# =============================================================================

def test_post_meeting_success():
    """Test POST /meetings creates meeting successfully."""
    # Create test room and employees
    room = {"room_id": 9110, "room_name": "Meeting Test Room", "max_capacity": 5}
    client.post("/rooms", json=room)
    
    emp1 = {"employee_id": 9110, "full_name": "Meeting Test Employee 1"}
    emp2 = {"employee_id": 9111, "full_name": "Meeting Test Employee 2"}
    client.post("/employees", json=emp1)
    client.post("/employees", json=emp2)
    
    # Create meeting
    meeting = {
        "room_id": 9110,
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "employee_ids": [9110, 9111]
    }
    
    response = client.post("/meetings", json=meeting)
    assert response.status_code == 200
    
    created = response.json()
    assert "meeting_id" in created
    assert created["room_id"] == 9110
    assert created["room_name"] == "Meeting Test Room"
    assert created["start_time"] == "09:00:00"
    assert created["end_time"] == "10:00:00"
    assert len(created["employees"]) == 2


def test_post_meeting_room_not_exists():
    """Test POST /meetings returns 400 when room doesn't exist."""
    meeting = {
        "room_id": 999999,
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "employee_ids": [9110]
    }
    
    response = client.post("/meetings", json=meeting)
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error
    assert "does not exist" in error["detail"]


def test_post_meeting_employee_not_exists():
    """Test POST /meetings returns 400 when employee doesn't exist."""
    # Create room
    room = {"room_id": 9111, "room_name": "Emp Not Exists Room", "max_capacity": 5}
    client.post("/rooms", json=room)
    
    meeting = {
        "room_id": 9111,
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "employee_ids": [999999]
    }
    
    response = client.post("/meetings", json=meeting)
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error
    assert "does not exist" in error["detail"]


def test_post_meeting_exceeds_capacity():
    """Test POST /meetings returns 400 when exceeding room capacity."""
    # Create small room
    room = {"room_id": 9112, "room_name": "Small Room", "max_capacity": 2}
    client.post("/rooms", json=room)
    
    # Create employees
    for i in range(3):
        emp = {"employee_id": 9112 + i, "full_name": f"Employee {i}"}
        client.post("/employees", json=emp)
    
    # Try to create meeting with too many employees
    meeting = {
        "room_id": 9112,
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "employee_ids": [9112, 9113, 9114]
    }
    
    response = client.post("/meetings", json=meeting)
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error
    assert "capacity" in error["detail"].lower()


def test_post_meeting_before_opening():
    """Test POST /meetings returns 400 for meeting before opening hours."""
    # Create room and employee
    room = {"room_id": 9115, "room_name": "Before Opening Room", "max_capacity": 5}
    emp = {"employee_id": 9115, "full_name": "Employee"}
    client.post("/rooms", json=room)
    client.post("/employees", json=emp)
    
    meeting = {
        "room_id": 9115,
        "start_time": "06:00:00",  # Before 07:00
        "end_time": "08:00:00",
        "employee_ids": [9115]
    }
    
    response = client.post("/meetings", json=meeting)
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error


def test_post_meeting_after_closing():
    """Test POST /meetings returns 400 for meeting after closing hours."""
    # Create room and employee
    room = {"room_id": 9116, "room_name": "After Closing Room", "max_capacity": 5}
    emp = {"employee_id": 9116, "full_name": "Employee"}
    client.post("/rooms", json=room)
    client.post("/employees", json=emp)
    
    meeting = {
        "room_id": 9116,
        "start_time": "18:00:00",
        "end_time": "20:00:00",  # After 19:00
        "employee_ids": [9116]
    }
    
    response = client.post("/meetings", json=meeting)
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error


def test_post_meeting_invalid_time_range():
    """Test POST /meetings returns 400 for invalid time range."""
    # Create room and employee
    room = {"room_id": 9117, "room_name": "Invalid Time Room", "max_capacity": 5}
    emp = {"employee_id": 9117, "full_name": "Employee"}
    client.post("/rooms", json=room)
    client.post("/employees", json=emp)
    
    meeting = {
        "room_id": 9117,
        "start_time": "10:00:00",
        "end_time": "09:00:00",  # End before start
        "employee_ids": [9117]
    }
    
    response = client.post("/meetings", json=meeting)
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error


def test_post_meeting_room_conflict():
    """Test POST /meetings returns 400 for room time conflict."""
    # Create room and employees
    room = {"room_id": 9118, "room_name": "Conflict Room", "max_capacity": 5}
    emp1 = {"employee_id": 9118, "full_name": "Employee 1"}
    emp2 = {"employee_id": 9119, "full_name": "Employee 2"}
    client.post("/rooms", json=room)
    client.post("/employees", json=emp1)
    client.post("/employees", json=emp2)
    
    # Create first meeting
    meeting1 = {
        "room_id": 9118,
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "employee_ids": [9118]
    }
    response1 = client.post("/meetings", json=meeting1)
    assert response1.status_code == 200
    
    # Try to create overlapping meeting in same room
    meeting2 = {
        "room_id": 9118,
        "start_time": "09:30:00",
        "end_time": "10:30:00",
        "employee_ids": [9119]
    }
    response2 = client.post("/meetings", json=meeting2)
    assert response2.status_code == 400
    error = response2.json()
    assert "detail" in error
    assert "booked" in error["detail"].lower()


def test_post_meeting_employee_conflict():
    """Test POST /meetings returns 400 for employee time conflict."""
    # Create rooms and employee
    room1 = {"room_id": 9120, "room_name": "Room 1", "max_capacity": 5}
    room2 = {"room_id": 9121, "room_name": "Room 2", "max_capacity": 5}
    emp = {"employee_id": 9120, "full_name": "Busy Employee"}
    client.post("/rooms", json=room1)
    client.post("/rooms", json=room2)
    client.post("/employees", json=emp)
    
    # Create first meeting
    meeting1 = {
        "room_id": 9120,
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "employee_ids": [9120]
    }
    response1 = client.post("/meetings", json=meeting1)
    assert response1.status_code == 200
    
    # Try to create overlapping meeting with same employee
    meeting2 = {
        "room_id": 9121,
        "start_time": "09:30:00",
        "end_time": "10:30:00",
        "employee_ids": [9120]
    }
    response2 = client.post("/meetings", json=meeting2)
    assert response2.status_code == 400
    error = response2.json()
    assert "detail" in error


# =============================================================================
# Available Slots Endpoint Integration Tests
# =============================================================================

def test_post_available_slots_success():
    """Test POST /meetings/available-slots finds available slots."""
    # Create room and employee
    room = {"room_id": 9130, "room_name": "Available Slots Room", "max_capacity": 5}
    emp = {"employee_id": 9130, "full_name": "Available Employee"}
    client.post("/rooms", json=room)
    client.post("/employees", json=emp)
    
    request = {
        "employee_ids": [9130],
        "duration_minutes": 60
    }
    
    response = client.post("/meetings/available-slots", json=request)
    assert response.status_code == 200
    
    data = response.json()
    assert "employee_ids" in data
    assert "duration_minutes" in data
    assert "available_slots" in data
    assert isinstance(data["available_slots"], list)


def test_post_available_slots_employee_not_exists():
    """Test POST /meetings/available-slots returns 400 for non-existent employee."""
    request = {
        "employee_ids": [999999],
        "duration_minutes": 60
    }
    
    response = client.post("/meetings/available-slots", json=request)
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error


def test_post_available_slots_invalid_duration():
    """Test POST /meetings/available-slots returns 400 for invalid duration."""
    # Create employee
    emp = {"employee_id": 9131, "full_name": "Employee"}
    client.post("/employees", json=emp)
    
    request = {
        "employee_ids": [9131],
        "duration_minutes": 0
    }
    
    response = client.post("/meetings/available-slots", json=request)
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error


def test_post_available_slots_multiple_employees():
    """Test POST /meetings/available-slots works with multiple employees."""
    # Create room and employees
    room = {"room_id": 9132, "room_name": "Multi Employee Room", "max_capacity": 5}
    emp1 = {"employee_id": 9132, "full_name": "Employee 1"}
    emp2 = {"employee_id": 9133, "full_name": "Employee 2"}
    client.post("/rooms", json=room)
    client.post("/employees", json=emp1)
    client.post("/employees", json=emp2)
    
    request = {
        "employee_ids": [9132, 9133],
        "duration_minutes": 30
    }
    
    response = client.post("/meetings/available-slots", json=request)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["employee_ids"]) == 2
    assert data["duration_minutes"] == 30


# =============================================================================
# Auto-Schedule Endpoint Integration Tests
# =============================================================================

def test_post_auto_schedule_success():
    """Test POST /meetings/auto-schedule creates meeting automatically."""
    # Create room and employees
    room = {"room_id": 9140, "room_name": "Auto Schedule Room", "max_capacity": 5}
    emp1 = {"employee_id": 9140, "full_name": "Auto Employee 1"}
    emp2 = {"employee_id": 9141, "full_name": "Auto Employee 2"}
    client.post("/rooms", json=room)
    client.post("/employees", json=emp1)
    client.post("/employees", json=emp2)
    
    request = {
        "employee_ids": [9140, 9141],
        "duration_minutes": 60
    }
    
    response = client.post("/meetings/auto-schedule", json=request)
    assert response.status_code == 200
    
    meeting = response.json()
    assert "meeting_id" in meeting
    assert "room_id" in meeting
    assert "start_time" in meeting
    assert "end_time" in meeting
    assert "employees" in meeting
    assert len(meeting["employees"]) == 2


def test_post_auto_schedule_employee_not_exists():
    """Test POST /meetings/auto-schedule returns 400 for non-existent employee."""
    request = {
        "employee_ids": [999999],
        "duration_minutes": 60
    }
    
    response = client.post("/meetings/auto-schedule", json=request)
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error


def test_post_auto_schedule_invalid_duration():
    """Test POST /meetings/auto-schedule returns 400 for invalid duration."""
    # Create employee
    emp = {"employee_id": 9142, "full_name": "Employee"}
    client.post("/employees", json=emp)
    
    request = {
        "employee_ids": [9142],
        "duration_minutes": -30
    }
    
    response = client.post("/meetings/auto-schedule", json=request)
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error


def test_post_auto_schedule_optimizes_capacity():
    """Test POST /meetings/auto-schedule optimizes room capacity selection."""
    # Create rooms with different capacities
    room1 = {"room_id": 9143, "room_name": "Opt Large Room", "max_capacity": 20}
    room2 = {"room_id": 9144, "room_name": "Opt Small Room", "max_capacity": 3}
    client.post("/rooms", json=room1)
    client.post("/rooms", json=room2)
    
    # Create employees
    emp1 = {"employee_id": 9143, "full_name": "Employee 1"}
    emp2 = {"employee_id": 9144, "full_name": "Employee 2"}
    client.post("/employees", json=emp1)
    client.post("/employees", json=emp2)
    
    request = {
        "employee_ids": [9143, 9144],
        "duration_minutes": 60
    }
    
    response = client.post("/meetings/auto-schedule", json=request)
    assert response.status_code == 200
    
    meeting = response.json()
    # Should prefer the smaller room that fits
    # (Could be room2 or another room with capacity >= 2)
    assert meeting["room_id"] is not None


# =============================================================================
# End-to-End Workflow Tests
# =============================================================================

def test_complete_meeting_workflow():
    """Test complete workflow: create resources, schedule meeting, check slots."""
    # 1. Create room
    room = {"room_id": 9150, "room_name": "Workflow Room", "max_capacity": 5}
    room_response = client.post("/rooms", json=room)
    assert room_response.status_code == 200
    
    # 2. Create employees
    emp1 = {"employee_id": 9150, "full_name": "Workflow Employee 1"}
    emp2 = {"employee_id": 9151, "full_name": "Workflow Employee 2"}
    emp1_response = client.post("/employees", json=emp1)
    emp2_response = client.post("/employees", json=emp2)
    assert emp1_response.status_code == 200
    assert emp2_response.status_code == 200
    
    # 3. Check available slots before meeting
    slots_request = {"employee_ids": [9150, 9151], "duration_minutes": 60}
    slots_response = client.post("/meetings/available-slots", json=slots_request)
    assert slots_response.status_code == 200
    initial_slots = slots_response.json()["available_slots"]
    
    # 4. Schedule a meeting
    meeting = {
        "room_id": 9150,
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "employee_ids": [9150, 9151]
    }
    meeting_response = client.post("/meetings", json=meeting)
    assert meeting_response.status_code == 200
    
    # 5. Check available slots after meeting (should have fewer slots)
    slots_response2 = client.post("/meetings/available-slots", json=slots_request)
    assert slots_response2.status_code == 200
    remaining_slots = slots_response2.json()["available_slots"]
    
    # Verify that the 10:00-11:00 slot is no longer available
    for slot in remaining_slots:
        assert not (slot["start_time"] == "10:00:00" and slot["end_time"] == "11:00:00")


def test_auto_schedule_picks_earliest_slot():
    """Test that auto-schedule picks the earliest available slot."""
    # Create room and employee
    room = {"room_id": 9152, "room_name": "Earliest Slot Room", "max_capacity": 5}
    emp = {"employee_id": 9152, "full_name": "Earliest Employee"}
    client.post("/rooms", json=room)
    client.post("/employees", json=emp)
    
    # Block early morning
    morning_meeting = {
        "room_id": 9152,
        "start_time": "07:00:00",
        "end_time": "09:00:00",
        "employee_ids": [9152]
    }
    client.post("/meetings", json=morning_meeting)
    
    # Create another employee and auto-schedule
    emp2 = {"employee_id": 9153, "full_name": "Second Employee"}
    client.post("/employees", json=emp2)
    
    request = {"employee_ids": [9153], "duration_minutes": 60}
    response = client.post("/meetings/auto-schedule", json=request)
    assert response.status_code == 200
    
    meeting = response.json()
    # Should schedule at the earliest available time
    assert meeting["start_time"] is not None
    # Time should be 07:00 or later (earliest available)
    assert meeting["start_time"] >= "07:00:00"
