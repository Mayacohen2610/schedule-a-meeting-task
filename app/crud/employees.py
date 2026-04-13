"""
CRUD operations for employees.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import schemas


def get_all_employees(db: Session) -> list[dict]:
    """
    Returns all employees from the employees table.
    Each employee includes employee_id and full_name.
    """
    result = db.execute(
        text("SELECT employee_id, full_name FROM employees ORDER BY employee_id")
    )
    rows = result.fetchall()
    return [
        {
            "employee_id": row[0],
            "full_name": row[1],
        }
        for row in rows
    ]


def create_employee(db: Session, employee: schemas.EmployeeCreate) -> dict:
    """
    Inserts a new employee into the employees table.
    Returns the created employee.
    """
    result = db.execute(
        text("""
            INSERT INTO employees (employee_id, full_name)
            VALUES (:employee_id, :full_name)
            RETURNING employee_id, full_name
        """),
        {
            "employee_id": employee.employee_id,
            "full_name": employee.full_name,
        },
    )
    db.commit()
    row = result.fetchone()
    return {
        "employee_id": row[0],
        "full_name": row[1],
    }


def get_employee_by_id(db: Session, employee_id: int) -> dict | None:
    """
    Returns an employee by id, or None if not found.
    """
    result = db.execute(
        text("SELECT employee_id, full_name FROM employees WHERE employee_id = :employee_id"),
        {"employee_id": employee_id}
    )
    row = result.fetchone()
    if row is None:
        return None
    return {
        "employee_id": row[0],
        "full_name": row[1],
    }
