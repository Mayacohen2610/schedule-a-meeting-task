"""
Utility functions for CRUD operations.
"""
from sqlalchemy import text


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


def check_time_overlap(start1, end1, start2, end2) -> bool:
    """
    Check if two time intervals overlap.
    Returns True if they overlap, False otherwise.
    """
    return start1 < end2 and start2 < end1
