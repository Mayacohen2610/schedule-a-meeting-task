"""
CRUD operations module.
Exports all CRUD functions from individual entity modules.
"""
from app.crud.items import get_all_items, create_item, update_item
from app.crud.employees import get_all_employees, create_employee, get_employee_by_id
from app.crud.rooms import get_all_rooms, create_room, get_room_by_id
from app.crud.meetings import (
    create_meeting,
    find_available_slots,
    schedule_best_meeting,
    schedule_best_available_meeting,
)
from app.crud.utils import check_db_connection, check_time_overlap

__all__ = [
    # Items
    "get_all_items",
    "create_item",
    "update_item",
    # Employees
    "get_all_employees",
    "create_employee",
    "get_employee_by_id",
    # Rooms
    "get_all_rooms",
    "create_room",
    "get_room_by_id",
    # Meetings
    "create_meeting",
    "find_available_slots",
    "schedule_best_meeting",
    "schedule_best_available_meeting",
    # Utils
    "check_db_connection",
    "check_time_overlap",
]
