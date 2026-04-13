"""
Room routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.get("/rooms")
def get_all_rooms(db: Session = Depends(get_db)):
    """
    Returns all rooms in the rooms table.
    Each room includes room_id, room_name, and max_capacity.
    """
    return crud.get_all_rooms(db)


@router.post("/rooms")
def add_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    """
    Adds a new room to the rooms table.
    Accepts room_id, room_name, and max_capacity.
    Returns the created room.
    """
    # Check if room already exists
    existing = crud.get_room_by_id(db, room.room_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Room with id {room.room_id} already exists")
    
    return crud.create_room(db, room)


@router.get("/rooms/{room_id}")
def get_room(room_id: int, db: Session = Depends(get_db)):
    """
    Returns a room by id.
    Returns 404 if no room exists with the given id.
    """
    room = crud.get_room_by_id(db, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room
