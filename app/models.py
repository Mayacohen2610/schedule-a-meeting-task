"""
SQLAlchemy models and table definitions.
"""
from sqlalchemy import Boolean, Column, Float, Integer, String, Time, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Item(Base):
    """ORM model for the items table."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)


class Employee(Base):
    """ORM model for the employees table."""

    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)


class Room(Base):
    """ORM model for the rooms table."""

    __tablename__ = "rooms"

    room_id = Column(Integer, primary_key=True)
    room_name = Column(String(255), nullable=False, unique=True)
    max_capacity = Column(Integer, nullable=False)


class Meeting(Base):
    """ORM model for the meetings table."""

    __tablename__ = "meetings"

    meeting_id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.room_id"), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # Relationship to room
    room = relationship("Room")


class EmployeeMeeting(Base):
    """ORM model for the employee_meetings junction table."""

    __tablename__ = "employee_meetings"

    employee_id = Column(Integer, ForeignKey("employees.employee_id"), primary_key=True)
    meeting_id = Column(Integer, ForeignKey("meetings.meeting_id"), primary_key=True)

    # Relationships
    employee = relationship("Employee")
    meeting = relationship("Meeting")