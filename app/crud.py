"""
CRUD operations for items. All SQL execution logic lives here.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import schemas


def check_db_connection() -> bool:
    """
    Verifies PostgreSQL connectivity.
    Returns True if database is reachable, False otherwise.
    """
    from app.database import engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_all_items(db: Session) -> list[dict]:
    """
    Returns all items from the items table.
    Each item includes id, item_name, category, price, and in_stock.
    """
    result = db.execute(
        text("SELECT id, item_name, category, price, in_stock FROM items ORDER BY id")
    )
    rows = result.fetchall()
    return [
        {
            "id": row[0],
            "item_name": row[1],
            "category": row[2],
            "price": row[3],
            "in_stock": row[4],
        }
        for row in rows
    ]


def create_item(db: Session, item: schemas.ItemCreate) -> dict:
    """
    Inserts a new item into the items table.
    Returns the created item with its assigned id.
    """
    result = db.execute(
        text("""
            INSERT INTO items (item_name, category, price, in_stock)
            VALUES (:item_name, :category, :price, :in_stock)
            RETURNING id, item_name, category, price, in_stock
        """),
        {
            "item_name": item.item_name,
            "category": item.category,
            "price": item.price,
            "in_stock": item.in_stock,
        },
    )
    db.commit()
    row = result.fetchone()
    return {
        "id": row[0],
        "item_name": row[1],
        "category": row[2],
        "price": row[3],
        "in_stock": row[4],
    }


def update_item(db: Session, item_id: int, update: schemas.ItemUpdate) -> dict | None:
    """
    Partially updates an item by id. Only provided fields are updated.
    Returns the updated item dict, or None if no item exists with the given id.
    Caller must ensure at least one field is provided.
    """
    updates = update.model_dump(exclude_unset=True)
    set_parts = [f"{k} = :{k}" for k in updates.keys()]
    set_clause = ", ".join(set_parts)
    params = dict(updates, item_id=item_id)

    result = db.execute(
        text(f"""
            UPDATE items
            SET {set_clause}
            WHERE id = :item_id
            RETURNING id, item_name, category, price, in_stock
        """),
        params,
    )
    db.commit()
    row = result.fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "item_name": row[1],
        "category": row[2],
        "price": row[3],
        "in_stock": row[4],
    }