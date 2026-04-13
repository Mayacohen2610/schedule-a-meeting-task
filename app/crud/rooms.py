"""
CRUD operations for rooms.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import schemas


def get_all_rooms(db: Session) -> list[dict]:
    """
    Returns all rooms from the rooms table.
    Each room includes room_id, room_name, and max_capacity.
    """
    result = db.execute(
        text("SELECT room_id, room_name, max_capacity FROM rooms ORDER BY room_id")
    )
    rows = result.fetchall()
    return [
        {
            "room_id": row[0],
            "room_name": row[1],
            "max_capacity": row[2],
        }
        for row in rows
    ]


def create_room(db: Session, room: schemas.RoomCreate) -> dict:
    """
    Inserts a new room into the rooms table.
    Returns the created room.
    """
    result = db.execute(
        text("""
            INSERT INTO rooms (room_id, room_name, max_capacity)
            VALUES (:room_id, :room_name, :max_capacity)
            RETURNING room_id, room_name, max_capacity
        """),
        {
            "room_id": room.room_id,
            "room_name": room.room_name,
            "max_capacity": room.max_capacity,
        },
    )
    db.commit()
    row = result.fetchone()
    return {
        "room_id": row[0],
        "room_name": row[1],
        "max_capacity": row[2],
    }


def get_room_by_id(db: Session, room_id: int) -> dict | None:
    """
    Returns a room by id, or None if not found.
    """
    result = db.execute(
        text("SELECT room_id, room_name, max_capacity FROM rooms WHERE room_id = :room_id"),
        {"room_id": room_id}
    )
    row = result.fetchone()
    if row is None:
        return None
    return {
        "room_id": row[0],
        "room_name": row[1],
        "max_capacity": row[2],
    }
