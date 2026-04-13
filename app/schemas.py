"""
Pydantic schemas for request/response validation.
"""
from typing import Optional
from datetime import time

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Request body for creating a new item."""

    item_name: str
    category: str
    price: float
    in_stock: bool = True


class ItemUpdate(BaseModel):
    """Request body for partial update of an item. All fields are optional."""

    price: Optional[float] = Field(default=None)
    in_stock: Optional[bool] = Field(default=None)


class ItemResponse(BaseModel):
    """Response schema for an item."""

    id: int
    item_name: str
    category: str
    price: float
    in_stock: bool


# Employee Schemas
class EmployeeCreate(BaseModel):
    """Request body for creating a new employee."""

    employee_id: int
    full_name: str


class EmployeeResponse(BaseModel):
    """Response schema for an employee."""

    employee_id: int
    full_name: str


# Room Schemas
class RoomCreate(BaseModel):
    """Request body for creating a new room."""

    room_id: int
    room_name: str
    max_capacity: int


class RoomResponse(BaseModel):
    """Response schema for a room."""

    room_id: int
    room_name: str
    max_capacity: int


# Meeting Schemas
class MeetingCreate(BaseModel):
    """Request body for creating a new meeting."""

    room_id: int
    start_time: time
    end_time: time
    employee_ids: list[int]


class MeetingResponse(BaseModel):
    """Response schema for a meeting."""

    meeting_id: int
    room_id: int
    room_name: str
    start_time: time
    end_time: time
    employees: list[EmployeeResponse]


# Available Slots Schemas
class AvailableSlotsRequest(BaseModel):
    """Request body for finding available time slots."""

    employee_ids: list[int]
    duration_minutes: int


class AvailableSlot(BaseModel):
    """A single available time slot with rooms."""

    start_time: time
    end_time: time
    available_rooms: list[RoomResponse]


class AvailableSlotsResponse(BaseModel):
    """Response schema for available slots query."""

    employee_ids: list[int]
    duration_minutes: int
    available_slots: list[AvailableSlot]


# Auto-schedule Schemas
class AutoScheduleRequest(BaseModel):
    """Request body for auto-scheduling a meeting."""

    employee_ids: list[int]
    duration_minutes: int