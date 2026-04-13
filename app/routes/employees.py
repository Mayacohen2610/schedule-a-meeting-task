"""
Employee routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.get("/employees")
def get_all_employees(db: Session = Depends(get_db)):
    """
    Returns all employees in the employees table.
    Each employee includes employee_id and full_name.
    """
    return crud.get_all_employees(db)


@router.post("/employees")
def add_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    """
    Adds a new employee to the employees table.
    Accepts employee_id and full_name.
    Returns the created employee.
    """
    # Check if employee already exists
    existing = crud.get_employee_by_id(db, employee.employee_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Employee with id {employee.employee_id} already exists")
    
    return crud.create_employee(db, employee)


@router.get("/employees/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    Returns an employee by id.
    Returns 404 if no employee exists with the given id.
    """
    employee = crud.get_employee_by_id(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee
