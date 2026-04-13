"""
API route definitions.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.get("/health")
def health():
    """
    Health check endpoint that verifies PostgreSQL connectivity.
    Returns {"status": "up"} when the database is reachable, {"status": "down"} otherwise.
    """
    if crud.check_db_connection():
        return {"status": "up"}
    return {"status": "down"}


@router.get("/items")
def get_all_items(db: Session = Depends(get_db)):
    """
    Returns all items in the items table.
    Each item includes id, item_name, category, price, and in_stock.
    """
    return crud.get_all_items(db)


@router.post("/items")
def add_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """
    Adds a new item to the items table.
    Accepts item_name, category, price, and optional in_stock (defaults to True).
    Returns the created item with its assigned id.
    """
    return crud.create_item(db, item)


@router.patch("/items/{item_id}")
def update_item(item_id: int, update: schemas.ItemUpdate, db: Session = Depends(get_db)):
    """
    Partially updates an item by its id. Only provided fields are updated.
    Supports price and/or in_stock; omitting a field leaves it unchanged.
    Returns the updated item, or 404 if no item exists with the given id.
    """
    updates = update.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = crud.update_item(db, item_id, update)
    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return result