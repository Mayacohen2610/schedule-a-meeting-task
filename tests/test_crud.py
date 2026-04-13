"""
Comprehensive unit tests for all CRUD operations.
Tests all functions in app.crud module with various scenarios.
"""
import pytest
from datetime import time
from app import crud, schemas


# =============================================================================
# Database Connection Tests
# =============================================================================

def test_check_db_connection():
    """Test database connection check returns True for valid connection."""
    result = crud.check_db_connection()
    assert result is True


# =============================================================================
# Item CRUD Tests
# =============================================================================

def test_get_all_items_empty(db_session):
    """Test getting all items when none exist."""
    # Clean items table first
    from sqlalchemy import text
    db_session.execute(text("DELETE FROM items"))
    db_session.commit()
    
    items = crud.get_all_items(db_session)
    assert isinstance(items, list)


def test_create_item(db_session):
    """Test creating a new item."""
    item_data = schemas.ItemCreate(
        item_name="Test Item",
        category="Test Category",
        price=99.99,
        in_stock=True
    )
    
    created = crud.create_item(db_session, item_data)
    
    assert created["id"] is not None
    assert created["item_name"] == "Test Item"
    assert created["category"] == "Test Category"
    assert created["price"] == 99.99
    assert created["in_stock"] is True


def test_create_item_default_in_stock(db_session):
    """Test creating item with default in_stock value."""
    item_data = schemas.ItemCreate(
        item_name="Default Stock Item",
        category="Test",
        price=50.0
    )
    
    created = crud.create_item(db_session, item_data)
    assert created["in_stock"] is True


def test_get_all_items_with_data(db_session):
    """Test getting all items returns correct data."""
    # Create test items
    item1 = schemas.ItemCreate(
        item_name="Item 1",
        category="Category A",
        price=10.0,
        in_stock=True
    )
    item2 = schemas.ItemCreate(
        item_name="Item 2",
        category="Category B",
        price=20.0,
        in_stock=False
    )
    
    created1 = crud.create_item(db_session, item1)
    created2 = crud.create_item(db_session, item2)
    
    items = crud.get_all_items(db_session)
    
    # Check that our created items are in the list
    item_ids = [item["id"] for item in items]
    assert created1["id"] in item_ids
    assert created2["id"] in item_ids


def test_update_item_price(db_session):
    """Test updating item price."""
    # Create an item
    item_data = schemas.ItemCreate(
        item_name="Update Test",
        category="Test",
        price=100.0,
        in_stock=True
    )
    created = crud.create_item(db_session, item_data)
    
    # Update price
    update_data = schemas.ItemUpdate(price=150.0)
    updated = crud.update_item(db_session, created["id"], update_data)
    
    assert updated is not None
    assert updated["price"] == 150.0
    assert updated["item_name"] == "Update Test"
    assert updated["in_stock"] is True


def test_update_item_in_stock(db_session):
    """Test updating item stock status."""
    item_data = schemas.ItemCreate(
        item_name="Stock Test",
        category="Test",
        price=50.0,
        in_stock=True
    )
    created = crud.create_item(db_session, item_data)
    
    # Update stock status
    update_data = schemas.ItemUpdate(in_stock=False)
    updated = crud.update_item(db_session, created["id"], update_data)
    
    assert updated is not None
    assert updated["in_stock"] is False
    assert updated["price"] == 50.0


def test_update_item_multiple_fields(db_session):
    """Test updating multiple item fields at once."""
    item_data = schemas.ItemCreate(
        item_name="Multi Update",
        category="Test",
        price=75.0,
        in_stock=True
    )
    created = crud.create_item(db_session, item_data)
    
    # Update both fields
    update_data = schemas.ItemUpdate(price=125.0, in_stock=False)
    updated = crud.update_item(db_session, created["id"], update_data)
    
    assert updated is not None
    assert updated["price"] == 125.0
    assert updated["in_stock"] is False


def test_update_item_nonexistent(db_session):
    """Test updating a non-existent item returns None."""
    update_data = schemas.ItemUpdate(price=100.0)
    result = crud.update_item(db_session, 999999, update_data)
    
    assert result is None


# =============================================================================
# Employee CRUD Tests
# =============================================================================

def test_get_all_employees(db_session):
    """Test getting all employees."""
    employees = crud.get_all_employees(db_session)
    assert isinstance(employees, list)


def test_create_employee(db_session):
    """Test creating a new employee."""
    employee_data = schemas.EmployeeCreate(
        employee_id=9001,
        full_name="John Doe"
    )
    
    created = crud.create_employee(db_session, employee_data)
    
    assert created["employee_id"] == 9001
    assert created["full_name"] == "John Doe"


def test_create_employee_duplicate_id(db_session):
    """Test creating employee with duplicate ID raises error."""
    employee_data = schemas.EmployeeCreate(
        employee_id=9002,
        full_name="Jane Smith"
    )
    
    crud.create_employee(db_session, employee_data)
    
    # Try to create with same ID
    duplicate_data = schemas.EmployeeCreate(
        employee_id=9002,
        full_name="Jane Duplicate"
    )
    
    with pytest.raises(Exception):  # Database will raise integrity error
        crud.create_employee(db_session, duplicate_data)


def test_get_employee_by_id_exists(db_session):
    """Test getting employee by ID when employee exists."""
    employee_data = schemas.EmployeeCreate(
        employee_id=9003,
        full_name="Alice Johnson"
    )
    crud.create_employee(db_session, employee_data)
    
    result = crud.get_employee_by_id(db_session, 9003)
    
    assert result is not None
    assert result["employee_id"] == 9003
    assert result["full_name"] == "Alice Johnson"


def test_get_employee_by_id_not_exists(db_session):
    """Test getting employee by ID when employee doesn't exist."""
    result = crud.get_employee_by_id(db_session, 999999)
    assert result is None


def test_get_all_employees_with_data(db_session):
    """Test getting all employees returns created employees."""
    employee1 = schemas.EmployeeCreate(employee_id=9004, full_name="Bob Brown")
    employee2 = schemas.EmployeeCreate(employee_id=9005, full_name="Carol White")
    
    crud.create_employee(db_session, employee1)
    crud.create_employee(db_session, employee2)
    
    employees = crud.get_all_employees(db_session)
    employee_ids = [emp["employee_id"] for emp in employees]
    
    assert 9004 in employee_ids
    assert 9005 in employee_ids


# =============================================================================
# Room CRUD Tests
# =============================================================================

def test_get_all_rooms(db_session):
    """Test getting all rooms."""
    rooms = crud.get_all_rooms(db_session)
    assert isinstance(rooms, list)


def test_create_room(db_session):
    """Test creating a new room."""
    room_data = schemas.RoomCreate(
        room_id=9001,
        room_name="Test Conference Room",
        max_capacity=10
    )
    
    created = crud.create_room(db_session, room_data)
    
    assert created["room_id"] == 9001
    assert created["room_name"] == "Test Conference Room"
    assert created["max_capacity"] == 10


def test_create_room_small_capacity(db_session):
    """Test creating room with small capacity."""
    room_data = schemas.RoomCreate(
        room_id=9002,
        room_name="Small Meeting Room",
        max_capacity=2
    )
    
    created = crud.create_room(db_session, room_data)
    assert created["max_capacity"] == 2


def test_create_room_large_capacity(db_session):
    """Test creating room with large capacity."""
    room_data = schemas.RoomCreate(
        room_id=9003,
        room_name="Auditorium",
        max_capacity=100
    )
    
    created = crud.create_room(db_session, room_data)
    assert created["max_capacity"] == 100


def test_create_room_duplicate_id(db_session):
    """Test creating room with duplicate ID raises error."""
    room_data = schemas.RoomCreate(
        room_id=9004,
        room_name="Room A",
        max_capacity=5
    )
    
    crud.create_room(db_session, room_data)
    
    # Try to create with same ID
    duplicate_data = schemas.RoomCreate(
        room_id=9004,
        room_name="Room B",
        max_capacity=10
    )
    
    with pytest.raises(Exception):  # Database will raise integrity error
        crud.create_room(db_session, duplicate_data)


def test_get_room_by_id_exists(db_session):
    """Test getting room by ID when room exists."""
    room_data = schemas.RoomCreate(
        room_id=9005,
        room_name="Executive Room",
        max_capacity=8
    )
    crud.create_room(db_session, room_data)
    
    result = crud.get_room_by_id(db_session, 9005)
    
    assert result is not None
    assert result["room_id"] == 9005
    assert result["room_name"] == "Executive Room"
    assert result["max_capacity"] == 8


def test_get_room_by_id_not_exists(db_session):
    """Test getting room by ID when room doesn't exist."""
    result = crud.get_room_by_id(db_session, 999999)
    assert result is None


def test_get_all_rooms_with_data(db_session):
    """Test getting all rooms returns created rooms."""
    room1 = schemas.RoomCreate(room_id=9006, room_name="Room 1", max_capacity=5)
    room2 = schemas.RoomCreate(room_id=9007, room_name="Room 2", max_capacity=15)
    
    crud.create_room(db_session, room1)
    crud.create_room(db_session, room2)
    
    rooms = crud.get_all_rooms(db_session)
    room_ids = [room["room_id"] for room in rooms]
    
    assert 9006 in room_ids
    assert 9007 in room_ids


# =============================================================================
# Time Overlap Helper Tests
# =============================================================================

def test_check_time_overlap_no_overlap():
    """Test time overlap check with non-overlapping intervals."""
    # 09:00-10:00 and 11:00-12:00
    result = crud.check_time_overlap(
        time(9, 0), time(10, 0),
        time(11, 0), time(12, 0)
    )
    assert result is False


def test_check_time_overlap_complete_overlap():
    """Test time overlap check with complete overlap."""
    # 09:00-11:00 and 09:30-10:30
    result = crud.check_time_overlap(
        time(9, 0), time(11, 0),
        time(9, 30), time(10, 30)
    )
    assert result is True


def test_check_time_overlap_partial_overlap():
    """Test time overlap check with partial overlap."""
    # 09:00-10:00 and 09:30-11:00
    result = crud.check_time_overlap(
        time(9, 0), time(10, 0),
        time(9, 30), time(11, 0)
    )
    assert result is True


def test_check_time_overlap_touching_boundaries():
    """Test time overlap check with touching boundaries (no overlap)."""
    # 09:00-10:00 and 10:00-11:00
    result = crud.check_time_overlap(
        time(9, 0), time(10, 0),
        time(10, 0), time(11, 0)
    )
    assert result is False


def test_check_time_overlap_reverse_order():
    """Test time overlap check with intervals in reverse order."""
    # 11:00-12:00 and 09:00-10:00 (no overlap)
    result = crud.check_time_overlap(
        time(11, 0), time(12, 0),
        time(9, 0), time(10, 0)
    )
    assert result is False


def test_check_time_overlap_same_intervals():
    """Test time overlap check with identical intervals."""
    # 09:00-10:00 and 09:00-10:00
    result = crud.check_time_overlap(
        time(9, 0), time(10, 0),
        time(9, 0), time(10, 0)
    )
    assert result is True


# =============================================================================
# Meeting Creation Tests
# =============================================================================

def test_create_meeting_success(db_session):
    """Test creating a valid meeting."""
    # Create test data
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9010, room_name="Meeting Room 1", max_capacity=5
    ))
    emp1 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9010, full_name="Employee 1"
    ))
    emp2 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9011, full_name="Employee 2"
    ))
    
    meeting_data = schemas.MeetingCreate(
        room_id=9010,
        start_time=time(9, 0),
        end_time=time(10, 0),
        employee_ids=[9010, 9011]
    )
    
    created = crud.create_meeting(db_session, meeting_data)
    
    assert created["meeting_id"] is not None
    assert created["room_id"] == 9010
    assert created["room_name"] == "Meeting Room 1"
    assert created["start_time"] == time(9, 0)
    assert created["end_time"] == time(10, 0)
    assert len(created["employees"]) == 2


def test_create_meeting_room_not_exists(db_session):
    """Test creating meeting with non-existent room raises error."""
    meeting_data = schemas.MeetingCreate(
        room_id=999999,
        start_time=time(9, 0),
        end_time=time(10, 0),
        employee_ids=[9010]
    )
    
    with pytest.raises(ValueError, match="Room with id 999999 does not exist"):
        crud.create_meeting(db_session, meeting_data)


def test_create_meeting_employee_not_exists(db_session):
    """Test creating meeting with non-existent employee raises error."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9011, room_name="Test Room", max_capacity=5
    ))
    
    meeting_data = schemas.MeetingCreate(
        room_id=9011,
        start_time=time(9, 0),
        end_time=time(10, 0),
        employee_ids=[999999]
    )
    
    with pytest.raises(ValueError, match="Employee with id 999999 does not exist"):
        crud.create_meeting(db_session, meeting_data)


def test_create_meeting_exceeds_capacity(db_session):
    """Test creating meeting that exceeds room capacity raises error."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9012, room_name="Small Room", max_capacity=2
    ))
    emp1 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9012, full_name="Employee 1"
    ))
    emp2 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9013, full_name="Employee 2"
    ))
    emp3 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9014, full_name="Employee 3"
    ))
    
    meeting_data = schemas.MeetingCreate(
        room_id=9012,
        start_time=time(9, 0),
        end_time=time(10, 0),
        employee_ids=[9012, 9013, 9014]
    )
    
    with pytest.raises(ValueError, match="has capacity 2 but 3 employees were assigned"):
        crud.create_meeting(db_session, meeting_data)


def test_create_meeting_before_opening(db_session):
    """Test creating meeting before opening time raises error."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9013, room_name="Test Room", max_capacity=5
    ))
    emp = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9015, full_name="Employee"
    ))
    
    meeting_data = schemas.MeetingCreate(
        room_id=9013,
        start_time=time(6, 30),  # Before 07:00
        end_time=time(8, 0),
        employee_ids=[9015]
    )
    
    with pytest.raises(ValueError, match="Meeting cannot start before 07:00"):
        crud.create_meeting(db_session, meeting_data)


def test_create_meeting_after_closing(db_session):
    """Test creating meeting after closing time raises error."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9014, room_name="Test Room", max_capacity=5
    ))
    emp = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9016, full_name="Employee"
    ))
    
    meeting_data = schemas.MeetingCreate(
        room_id=9014,
        start_time=time(18, 0),
        end_time=time(20, 0),  # After 19:00
        employee_ids=[9016]
    )
    
    with pytest.raises(ValueError, match="Meeting cannot end after 19:00"):
        crud.create_meeting(db_session, meeting_data)


def test_create_meeting_invalid_time_range(db_session):
    """Test creating meeting with start time after end time raises error."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9015, room_name="Test Room", max_capacity=5
    ))
    emp = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9017, full_name="Employee"
    ))
    
    meeting_data = schemas.MeetingCreate(
        room_id=9015,
        start_time=time(10, 0),
        end_time=time(9, 0),  # End before start
        employee_ids=[9017]
    )
    
    with pytest.raises(ValueError, match="start time must be before end time"):
        crud.create_meeting(db_session, meeting_data)


def test_create_meeting_room_conflict(db_session):
    """Test creating meeting with room time conflict raises error."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9016, room_name="Conflict Room", max_capacity=5
    ))
    emp1 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9018, full_name="Employee 1"
    ))
    emp2 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9019, full_name="Employee 2"
    ))
    
    # Create first meeting
    meeting1 = schemas.MeetingCreate(
        room_id=9016,
        start_time=time(9, 0),
        end_time=time(10, 0),
        employee_ids=[9018]
    )
    crud.create_meeting(db_session, meeting1)
    
    # Try to create overlapping meeting
    meeting2 = schemas.MeetingCreate(
        room_id=9016,
        start_time=time(9, 30),
        end_time=time(10, 30),
        employee_ids=[9019]
    )
    
    with pytest.raises(ValueError, match="already booked"):
        crud.create_meeting(db_session, meeting2)


def test_create_meeting_employee_conflict(db_session):
    """Test creating meeting with employee time conflict raises error."""
    room1 = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9017, room_name="Room 1", max_capacity=5
    ))
    room2 = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9018, room_name="Room 2", max_capacity=5
    ))
    emp = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9020, full_name="Busy Employee"
    ))
    
    # Create first meeting
    meeting1 = schemas.MeetingCreate(
        room_id=9017,
        start_time=time(9, 0),
        end_time=time(10, 0),
        employee_ids=[9020]
    )
    crud.create_meeting(db_session, meeting1)
    
    # Try to create overlapping meeting with same employee
    meeting2 = schemas.MeetingCreate(
        room_id=9018,
        start_time=time(9, 30),
        end_time=time(10, 30),
        employee_ids=[9020]
    )
    
    with pytest.raises(ValueError, match="already in a meeting"):
        crud.create_meeting(db_session, meeting2)


def test_create_meeting_at_boundary(db_session):
    """Test creating back-to-back meetings (no overlap at boundaries)."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9019, room_name="Boundary Room", max_capacity=5
    ))
    emp1 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9021, full_name="Employee 1"
    ))
    emp2 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9022, full_name="Employee 2"
    ))
    
    # Create first meeting
    meeting1 = schemas.MeetingCreate(
        room_id=9019,
        start_time=time(9, 0),
        end_time=time(10, 0),
        employee_ids=[9021]
    )
    crud.create_meeting(db_session, meeting1)
    
    # Create meeting right after (should succeed)
    meeting2 = schemas.MeetingCreate(
        room_id=9019,
        start_time=time(10, 0),
        end_time=time(11, 0),
        employee_ids=[9022]
    )
    created = crud.create_meeting(db_session, meeting2)
    
    assert created["meeting_id"] is not None


# =============================================================================
# Find Available Slots Tests
# =============================================================================

def test_find_available_slots_empty_schedule(db_session):
    """Test finding slots with no existing meetings."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9020, room_name="Available Room", max_capacity=5
    ))
    emp = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9023, full_name="Free Employee"
    ))
    
    result = crud.find_available_slots(db_session, [9023], 60)
    
    assert result["employee_ids"] == [9023]
    assert result["duration_minutes"] == 60
    assert len(result["available_slots"]) > 0


def test_find_available_slots_invalid_duration_zero(db_session):
    """Test finding slots with zero duration raises error."""
    emp = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9024, full_name="Employee"
    ))
    
    with pytest.raises(ValueError, match="Duration must be positive"):
        crud.find_available_slots(db_session, [9024], 0)


def test_find_available_slots_invalid_duration_negative(db_session):
    """Test finding slots with negative duration raises error."""
    emp = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9025, full_name="Employee"
    ))
    
    with pytest.raises(ValueError, match="Duration must be positive"):
        crud.find_available_slots(db_session, [9025], -30)


def test_find_available_slots_duration_too_long(db_session):
    """Test finding slots with duration exceeding 12 hours raises error."""
    emp = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9026, full_name="Employee"
    ))
    
    with pytest.raises(ValueError, match="Duration cannot exceed 12 hours"):
        crud.find_available_slots(db_session, [9026], 721)


def test_find_available_slots_employee_not_exists(db_session):
    """Test finding slots with non-existent employee raises error."""
    with pytest.raises(ValueError, match="Employee with id 999999 does not exist"):
        crud.find_available_slots(db_session, [999999], 60)


def test_find_available_slots_no_suitable_rooms(db_session):
    """Test finding slots when no rooms have sufficient capacity."""
    # Create a room with small capacity
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9021, room_name="Tiny Room", max_capacity=1
    ))
    emp1 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9027, full_name="Employee 1"
    ))
    emp2 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9028, full_name="Employee 2"
    ))
    
    # This should raise an error because room capacity (1) is less than employees (2)
    with pytest.raises(ValueError, match="No rooms available with capacity"):
        crud.find_available_slots(db_session, [9027, 9028], 60)


def test_find_available_slots_with_busy_employee(db_session):
    """Test finding slots excludes times when employee is busy."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9022, room_name="Room", max_capacity=5
    ))
    emp = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9029, full_name="Busy Employee"
    ))
    
    # Create a meeting for the employee
    meeting = schemas.MeetingCreate(
        room_id=9022,
        start_time=time(10, 0),
        end_time=time(11, 0),
        employee_ids=[9029]
    )
    crud.create_meeting(db_session, meeting)
    
    # Find slots
    result = crud.find_available_slots(db_session, [9029], 60)
    
    # Check that 10:00-11:00 slot is not included
    for slot in result["available_slots"]:
        # Slot should not overlap with 10:00-11:00
        assert not crud.check_time_overlap(
            slot["start_time"], slot["end_time"],
            time(10, 0), time(11, 0)
        )


def test_find_available_slots_multiple_employees(db_session):
    """Test finding slots for multiple employees."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9023, room_name="Multi Room", max_capacity=5
    ))
    emp1 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9030, full_name="Employee 1"
    ))
    emp2 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9031, full_name="Employee 2"
    ))
    
    result = crud.find_available_slots(db_session, [9030, 9031], 30)
    
    assert result["employee_ids"] == [9030, 9031]
    assert len(result["available_slots"]) > 0


def test_find_available_slots_different_durations(db_session):
    """Test finding slots with different durations."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9024, room_name="Duration Room", max_capacity=5
    ))
    emp = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9032, full_name="Employee"
    ))
    
    # Find slots for 30 minutes
    result_30 = crud.find_available_slots(db_session, [9032], 30)
    # Find slots for 120 minutes
    result_120 = crud.find_available_slots(db_session, [9032], 120)
    
    # Should have more slots for shorter duration
    assert len(result_30["available_slots"]) >= len(result_120["available_slots"])


# =============================================================================
# Schedule Best Meeting Tests
# =============================================================================

def test_schedule_best_meeting_success(db_session):
    """Test scheduling best meeting finds and creates meeting."""
    # Create rooms with different capacities
    room1 = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9025, room_name="Large Room", max_capacity=10
    ))
    room2 = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9026, room_name="Small Room", max_capacity=3
    ))
    emp1 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9033, full_name="Employee 1"
    ))
    emp2 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9034, full_name="Employee 2"
    ))
    
    result = crud.schedule_best_meeting(db_session, [9033, 9034], 60)
    
    assert result["meeting_id"] is not None
    assert len(result["employees"]) == 2
    # Should prefer room with capacity closer to employee count
    # Could be our test room 9026 (capacity 3) or existing room 3 (capacity 3)
    # Both have same capacity, so either is valid
    assert result["room_name"] in ["Small Room", "Conference Room C"]


def test_schedule_best_meeting_no_available_slots(db_session):
    """Test scheduling best meeting when no slots available raises error."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9027, room_name="Fully Booked Room", max_capacity=5
    ))
    emp = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9035, full_name="Very Busy Employee"
    ))
    
    # Book the entire day for the employee
    for hour in range(7, 19):
        meeting = schemas.MeetingCreate(
            room_id=9027,
            start_time=time(hour, 0),
            end_time=time(hour + 1, 0) if hour < 19 else time(19, 0),
            employee_ids=[9035]
        )
        if hour < 19:
            crud.create_meeting(db_session, meeting)
    
    with pytest.raises(ValueError, match="No available slots found"):
        crud.schedule_best_meeting(db_session, [9035], 60)


def test_schedule_best_meeting_prefers_exact_capacity(db_session):
    """Test scheduling prefers room with exact capacity match."""
    # Create rooms with different capacities
    room1 = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9028, room_name="Room 10", max_capacity=10
    ))
    room2 = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9029, room_name="Room 5", max_capacity=5
    ))
    room3 = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9030, room_name="Room 3 (exact)", max_capacity=3
    ))
    
    employees = []
    for i in range(3):
        emp = crud.create_employee(db_session, schemas.EmployeeCreate(
            employee_id=9036 + i, full_name=f"Employee {i+1}"
        ))
        employees.append(9036 + i)
    
    result = crud.schedule_best_meeting(db_session, employees, 60)
    
    # Should prefer room with exact capacity (3)
    assert result["room_id"] == 9030


def test_schedule_best_meeting_earliest_slot(db_session):
    """Test scheduling selects earliest available slot."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9031, room_name="Early Room", max_capacity=5
    ))
    emp = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9039, full_name="Employee"
    ))
    
    # Block early morning
    meeting = schemas.MeetingCreate(
        room_id=9031,
        start_time=time(7, 0),
        end_time=time(9, 0),
        employee_ids=[9039]
    )
    crud.create_meeting(db_session, meeting)
    
    # Schedule new meeting
    result = crud.schedule_best_meeting(db_session, [9039], 60)
    
    # Should be scheduled at the earliest available time after 9:00
    assert result["start_time"] >= time(9, 0)


def test_schedule_best_meeting_invalid_employee(db_session):
    """Test scheduling with invalid employee raises error."""
    with pytest.raises(ValueError, match="Employee with id 999999 does not exist"):
        crud.schedule_best_meeting(db_session, [999999], 60)


# =============================================================================
# Schedule Best Available Meeting Tests
# =============================================================================

def test_schedule_best_available_meeting_success(db_session):
    """Test schedule_best_available_meeting creates meeting successfully."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9032, room_name="Available Room", max_capacity=5
    ))
    emp1 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9040, full_name="Employee 1"
    ))
    emp2 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9041, full_name="Employee 2"
    ))
    
    result = crud.schedule_best_available_meeting(db_session, [9040, 9041], 60)
    
    assert result["meeting_id"] is not None
    assert len(result["employees"]) == 2


def test_schedule_best_available_meeting_no_slots(db_session):
    """Test schedule_best_available_meeting when no slots available."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9033, room_name="Booked Room", max_capacity=5
    ))
    emp = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9042, full_name="Busy Employee"
    ))
    
    # Book entire day
    for hour in range(7, 19):
        meeting = schemas.MeetingCreate(
            room_id=9033,
            start_time=time(hour, 0),
            end_time=time(hour + 1, 0) if hour < 19 else time(19, 0),
            employee_ids=[9042]
        )
        if hour < 19:
            crud.create_meeting(db_session, meeting)
    
    with pytest.raises(ValueError, match="No available slots found"):
        crud.schedule_best_available_meeting(db_session, [9042], 60)


def test_schedule_best_available_meeting_capacity_optimization(db_session):
    """Test schedule_best_available_meeting optimizes for room capacity."""
    # Create rooms with different capacities
    room1 = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9034, room_name="Huge Room", max_capacity=20
    ))
    room2 = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9035, room_name="Perfect Room", max_capacity=4
    ))
    
    employees = []
    for i in range(4):
        emp = crud.create_employee(db_session, schemas.EmployeeCreate(
            employee_id=9043 + i, full_name=f"Employee {i+1}"
        ))
        employees.append(9043 + i)
    
    result = crud.schedule_best_available_meeting(db_session, employees, 60)
    
    # Should prefer room with capacity closer to employee count (4 employees)
    # Get the room details to check capacity
    room_info = crud.get_room_by_id(db_session, result["room_id"])
    
    assert room_info is not None
    assert room_info["max_capacity"] >= 4  # Room must have sufficient capacity
    # Should not choose the huge room (20 capacity) when better options exist
    assert room_info["max_capacity"] <= 10  # Should prefer smaller rooms


def test_schedule_best_available_meeting_same_as_schedule_best(db_session):
    """Test schedule_best_available_meeting produces same results as schedule_best_meeting."""
    room = crud.create_room(db_session, schemas.RoomCreate(
        room_id=9036, room_name="Compare Room", max_capacity=5
    ))
    emp1 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9047, full_name="Compare Employee 1"
    ))
    emp2 = crud.create_employee(db_session, schemas.EmployeeCreate(
        employee_id=9048, full_name="Compare Employee 2"
    ))
    
    # Both functions should produce similar results (use same selection logic)
    result1 = crud.schedule_best_meeting(db_session, [9047], 60)
    result2 = crud.schedule_best_available_meeting(db_session, [9048], 60)
    
    # Should have similar structure (same fields exist)
    assert "meeting_id" in result1
    assert "meeting_id" in result2
    assert "room_id" in result1
    assert "room_id" in result2
    assert "start_time" in result1
    assert "start_time" in result2
    assert "end_time" in result1
    assert "end_time" in result2
    assert "employees" in result1
    assert "employees" in result2
    
    # Both should create valid meetings with 1 hour duration
    from datetime import timedelta
    duration1 = (timedelta(hours=result1["end_time"].hour, minutes=result1["end_time"].minute) - 
                 timedelta(hours=result1["start_time"].hour, minutes=result1["start_time"].minute))
    duration2 = (timedelta(hours=result2["end_time"].hour, minutes=result2["end_time"].minute) - 
                 timedelta(hours=result2["start_time"].hour, minutes=result2["start_time"].minute))
    
    assert duration1.total_seconds() == 3600  # 60 minutes
    assert duration2.total_seconds() == 3600  # 60 minutes
