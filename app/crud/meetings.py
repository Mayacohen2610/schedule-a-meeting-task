"""
CRUD operations for meetings.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import time as time_type, datetime, timedelta

from app import schemas
from app.crud.employees import get_employee_by_id
from app.crud.rooms import get_room_by_id, get_all_rooms
from app.crud.utils import check_time_overlap

# Define operating hours
OPENING_TIME = time_type(7, 0)   # 07:00
CLOSING_TIME = time_type(19, 0)  # 19:00


def create_meeting(db: Session, meeting: schemas.MeetingCreate) -> dict:
    """
    Creates a new meeting with validations:
    1. Validates room exists and gets capacity
    2. Validates all employees exist
    3. Checks room capacity
    4. Validates time is within 07:00-19:00
    5. Checks for room time conflicts
    6. Checks for employee time conflicts
    7. Inserts meeting and employee_meetings records
    8. Returns the created meeting with all details
    """
    # 1. Validate room exists and get capacity
    room = get_room_by_id(db, meeting.room_id)
    if room is None:
        raise ValueError(f"Room with id {meeting.room_id} does not exist")
    
    # 2. Validate all employees exist
    employees = []
    for emp_id in meeting.employee_ids:
        employee = get_employee_by_id(db, emp_id)
        if employee is None:
            raise ValueError(f"Employee with id {emp_id} does not exist")
        employees.append(employee)
    
    # 3. Check room capacity
    if len(meeting.employee_ids) > room["max_capacity"]:
        raise ValueError(
            f"Room '{room['room_name']}' has capacity {room['max_capacity']} "
            f"but {len(meeting.employee_ids)} employees were assigned"
        )
    
    # 4. Validate time is within operating hours (07:00-19:00)
    if meeting.start_time < OPENING_TIME:
        raise ValueError(f"Meeting cannot start before {OPENING_TIME.strftime('%H:%M')}")
    
    if meeting.end_time > CLOSING_TIME:
        raise ValueError(f"Meeting cannot end after {CLOSING_TIME.strftime('%H:%M')}")
    
    if meeting.start_time >= meeting.end_time:
        raise ValueError("Meeting start time must be before end time")
    
    # 5. Check for room time conflicts using interval overlap
    result = db.execute(
        text("""
            SELECT meeting_id, start_time, end_time
            FROM meetings
            WHERE room_id = :room_id
        """),
        {"room_id": meeting.room_id}
    )
    existing_meetings = result.fetchall()
    
    for existing in existing_meetings:
        if check_time_overlap(
            meeting.start_time, meeting.end_time,
            existing[1], existing[2]
        ):
            raise ValueError(
                f"Room '{room['room_name']}' is already booked from "
                f"{existing[1].strftime('%H:%M')} to {existing[2].strftime('%H:%M')}"
            )
    
    # 6. Check for employee time conflicts
    for emp_id in meeting.employee_ids:
        result = db.execute(
            text("""
                SELECT m.meeting_id, m.start_time, m.end_time
                FROM meetings m
                JOIN employee_meetings em ON m.meeting_id = em.meeting_id
                WHERE em.employee_id = :employee_id
            """),
            {"employee_id": emp_id}
        )
        employee_meetings = result.fetchall()
        
        for existing in employee_meetings:
            if check_time_overlap(
                meeting.start_time, meeting.end_time,
                existing[1], existing[2]
            ):
                # Find employee name for better error message
                emp_name = next(e["full_name"] for e in employees if e["employee_id"] == emp_id)
                raise ValueError(
                    f"Employee '{emp_name}' is already in a meeting from "
                    f"{existing[1].strftime('%H:%M')} to {existing[2].strftime('%H:%M')}"
                )
    
    # 7. Insert meeting
    result = db.execute(
        text("""
            INSERT INTO meetings (room_id, start_time, end_time)
            VALUES (:room_id, :start_time, :end_time)
            RETURNING meeting_id
        """),
        {
            "room_id": meeting.room_id,
            "start_time": meeting.start_time,
            "end_time": meeting.end_time,
        }
    )
    meeting_id = result.fetchone()[0]
    
    # 8. Insert employee_meetings records
    for emp_id in meeting.employee_ids:
        db.execute(
            text("""
                INSERT INTO employee_meetings (employee_id, meeting_id)
                VALUES (:employee_id, :meeting_id)
            """),
            {
                "employee_id": emp_id,
                "meeting_id": meeting_id,
            }
        )
    
    db.commit()
    
    # 9. Return the created meeting with all details
    return {
        "meeting_id": meeting_id,
        "room_id": room["room_id"],
        "room_name": room["room_name"],
        "start_time": meeting.start_time,
        "end_time": meeting.end_time,
        "employees": employees,
    }


def find_available_slots(db: Session, employee_ids: list[int], duration_minutes: int) -> dict:
    """
    Finds all available time slots for a group of employees with a specific duration.
    
    Algorithm:
    1. Validate all employees exist
    2. Get all busy time intervals for these employees (merge overlapping intervals)
    3. Get all rooms
    4. Generate potential time slots (every 30 minutes from 07:00 to 19:00)
    5. For each slot:
       - Check if all employees are available
       - Find which rooms are available (have capacity and not booked)
    6. Return list of slots with available rooms
    """
    # Validate duration
    if duration_minutes <= 0:
        raise ValueError("Duration must be positive")
    
    if duration_minutes > 720:  # 12 hours
        raise ValueError("Duration cannot exceed 12 hours")
    
    # 1. Validate all employees exist
    employees = []
    for emp_id in employee_ids:
        employee = get_employee_by_id(db, emp_id)
        if employee is None:
            raise ValueError(f"Employee with id {emp_id} does not exist")
        employees.append(employee)
    
    # 2. Get all busy intervals for employees and merge them
    busy_intervals = []
    for emp_id in employee_ids:
        result = db.execute(
            text("""
                SELECT m.start_time, m.end_time
                FROM meetings m
                JOIN employee_meetings em ON m.meeting_id = em.meeting_id
                WHERE em.employee_id = :employee_id
                ORDER BY m.start_time
            """),
            {"employee_id": emp_id}
        )
        for row in result.fetchall():
            busy_intervals.append((row[0], row[1]))
    
    # Merge overlapping busy intervals
    if busy_intervals:
        busy_intervals.sort()
        merged_busy = [busy_intervals[0]]
        for start, end in busy_intervals[1:]:
            last_start, last_end = merged_busy[-1]
            if start <= last_end:
                # Overlapping or adjacent - merge
                merged_busy[-1] = (last_start, max(end, last_end))
            else:
                merged_busy.append((start, end))
    else:
        merged_busy = []
    
    # 3. Get all rooms
    all_rooms = get_all_rooms(db)
    
    # Filter rooms that have sufficient capacity
    suitable_rooms = [r for r in all_rooms if r["max_capacity"] >= len(employee_ids)]
    
    if not suitable_rooms:
        raise ValueError(
            f"No rooms available with capacity for {len(employee_ids)} employees. "
            f"Maximum room capacity is {max(r['max_capacity'] for r in all_rooms)}"
        )
    
    # 4. Generate potential time slots (every 30 minutes)
    slots = []
    current_datetime = datetime.combine(datetime.today(), OPENING_TIME)
    end_datetime = datetime.combine(datetime.today(), CLOSING_TIME)
    duration_delta = timedelta(minutes=duration_minutes)
    slot_increment = timedelta(minutes=30)
    
    while current_datetime + duration_delta <= end_datetime:
        slot_start = current_datetime.time()
        slot_end = (current_datetime + duration_delta).time()
        
        # 5. Check if employees are available in this slot
        employees_available = True
        for busy_start, busy_end in merged_busy:
            if check_time_overlap(slot_start, slot_end, busy_start, busy_end):
                employees_available = False
                break
        
        if employees_available:
            # 6. Find which rooms are available for this slot
            available_rooms = []
            for room in suitable_rooms:
                # Check if room is free during this slot
                result = db.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM meetings
                        WHERE room_id = :room_id
                        AND (
                            (start_time < :slot_end AND end_time > :slot_start)
                        )
                    """),
                    {
                        "room_id": room["room_id"],
                        "slot_start": slot_start,
                        "slot_end": slot_end,
                    }
                )
                conflicts = result.fetchone()[0]
                
                if conflicts == 0:
                    available_rooms.append(room)
            
            # Only add slot if at least one room is available
            if available_rooms:
                slots.append({
                    "start_time": slot_start,
                    "end_time": slot_end,
                    "available_rooms": available_rooms,
                })
        
        current_datetime += slot_increment
    
    return {
        "employee_ids": employee_ids,
        "duration_minutes": duration_minutes,
        "available_slots": slots,
    }


def schedule_best_meeting(db: Session, employee_ids: list[int], duration_minutes: int) -> dict:
    """
    Automatically schedules a meeting by finding and booking the best available slot.
    
    Best slot selection criteria:
    1. Room with capacity closest to the number of employees (minimize waste)
    2. Earliest available time slot
    
    Returns the created meeting or raises ValueError if no slots available.
    """
    # Find all available slots
    slots_result = find_available_slots(db, employee_ids, duration_minutes)
    
    if not slots_result["available_slots"]:
        raise ValueError("No available slots found for the requested employees and duration")
    
    num_employees = len(employee_ids)
    
    # Find the best slot and room combination
    best_slot = None
    best_room = None
    min_capacity_diff = float('inf')
    
    for slot in slots_result["available_slots"]:
        # Sort rooms by capacity difference (closest to employee count)
        for room in slot["available_rooms"]:
            capacity_diff = room["max_capacity"] - num_employees
            
            # We want the smallest non-negative difference
            if capacity_diff >= 0 and capacity_diff < min_capacity_diff:
                min_capacity_diff = capacity_diff
                best_slot = slot
                best_room = room
                # Found a room with exact capacity match, no need to continue
                if capacity_diff == 0:
                    break
        
        # If we found an exact match, use the first slot with exact match
        if min_capacity_diff == 0:
            break
    
    if not best_slot or not best_room:
        raise ValueError("Could not determine best slot and room")
    
    # Create the meeting using the best slot and room
    meeting = schemas.MeetingCreate(
        room_id=best_room["room_id"],
        start_time=best_slot["start_time"],
        end_time=best_slot["end_time"],
        employee_ids=employee_ids
    )
    
    return create_meeting(db, meeting)


def schedule_best_available_meeting(db: Session, employee_ids: list[int], duration_minutes: int) -> dict:
    """
    Finds the best available slot and automatically schedules a meeting.
    
    This is an alias for schedule_best_meeting() for backward compatibility.
    
    Best slot selection criteria:
    1. Room with capacity closest to the number of employees (minimize waste)
    2. Earliest available time slot
    
    Returns the created meeting or raises ValueError if no slots available.
    """
    return schedule_best_meeting(db, employee_ids, duration_minutes)
