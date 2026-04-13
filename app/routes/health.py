"""
Health check routes.
"""
from fastapi import APIRouter

from app import crud

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
