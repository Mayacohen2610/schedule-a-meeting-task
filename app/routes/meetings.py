"""
Meeting routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.post("/meetings")
def schedule_meeting(meeting: schemas.MeetingCreate, db: Session = Depends(get_db)):
    """
    Schedules a new meeting with validations:
    - Room must exist and have sufficient capacity
    - All employees must exist
    - Time must be within 07:00-19:00
    - No room conflicts (room not double-booked)
    - No employee conflicts (employee not in two meetings at once)
    
    Returns the created meeting with all details.
    """
    try:
        return crud.create_meeting(db, meeting)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/meetings/available-slots")
def find_available_slots(request: schemas.AvailableSlotsRequest, db: Session = Depends(get_db)):
    """
    Finds available time slots for a group of employees with a specific duration.
    
    Returns a list of time slots where:
    - All requested employees are available
    - At least one room with sufficient capacity is available
    
    Slots are generated every 30 minutes from 07:00 to 19:00.
    """
    try:
        return crud.find_available_slots(db, request.employee_ids, request.duration_minutes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/meetings/auto-schedule")
def auto_schedule_meeting(request: schemas.AutoScheduleRequest, db: Session = Depends(get_db)):
    """
    Automatically schedules a meeting by finding and booking the best available slot.
    
    Selection criteria:
    1. Room with capacity closest to the number of employees (minimize waste)
    2. Earliest available time slot
    
    Returns the created meeting with all details.
    """
    try:
        return crud.schedule_best_meeting(db, request.employee_ids, request.duration_minutes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
