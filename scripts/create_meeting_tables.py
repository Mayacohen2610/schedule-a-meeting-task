"""
Script to create the meeting scheduling tables and load initial data from CSV files.
This should be run once to set up the database schema and populate it with initial data.
"""
import csv
import sys
from datetime import time
from pathlib import Path

# Add parent directory to path so we can import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models import Base


def create_tables():
    """Create all tables defined in models."""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


def load_rooms_from_csv():
    """Load rooms from the rooms.csv file."""
    print("Loading rooms from CSV...")
    csv_path = Path(__file__).parent.parent / "resources" / "rooms.csv"
    
    db = SessionLocal()
    try:
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                db.execute(
                    text("""
                        INSERT INTO rooms (room_id, room_name, max_capacity)
                        VALUES (:room_id, :room_name, :max_capacity)
                        ON CONFLICT (room_id) DO NOTHING
                    """),
                    {
                        "room_id": int(row["room_id"]),
                        "room_name": row["room_name"],
                        "max_capacity": int(row["max_capacity"]),
                    }
                )
        db.commit()
        print(f"Rooms loaded successfully!")
    except Exception as e:
        print(f"Error loading rooms: {e}")
        db.rollback()
    finally:
        db.close()


def load_meetings_from_csv():
    """Load meetings and employees from the meetings.csv file."""
    print("Loading meetings and employees from CSV...")
    csv_path = Path(__file__).parent.parent / "resources" / "meetings.csv"
    
    db = SessionLocal()
    try:
        # First, collect unique employees
        employees = {}
        meetings_data = []
        
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                employee_id = int(row["employee_id"])
                employees[employee_id] = row["full_name"]
                meetings_data.append(row)
        
        # Insert employees
        print(f"Inserting {len(employees)} unique employees...")
        for employee_id, full_name in employees.items():
            db.execute(
                text("""
                    INSERT INTO employees (employee_id, full_name)
                    VALUES (:employee_id, :full_name)
                    ON CONFLICT (employee_id) DO NOTHING
                """),
                {
                    "employee_id": employee_id,
                    "full_name": full_name,
                }
            )
        db.commit()
        
        # Group meetings by time and room
        meetings_by_key = {}
        for row in meetings_data:
            key = (row["start_time"], row["end_time"], row["room_name"])
            if key not in meetings_by_key:
                meetings_by_key[key] = []
            meetings_by_key[key].append(int(row["employee_id"]))
        
        # Insert meetings and employee_meetings
        print(f"Inserting {len(meetings_by_key)} meetings...")
        for (start_time_str, end_time_str, room_name), employee_ids in meetings_by_key.items():
            # Get room_id by room_name
            result = db.execute(
                text("SELECT room_id FROM rooms WHERE room_name = :room_name"),
                {"room_name": room_name}
            )
            room = result.fetchone()
            if not room:
                print(f"Warning: Room '{room_name}' not found, skipping meeting")
                continue
            
            room_id = room[0]
            
            # Parse time strings (format: HH:MM)
            start_hour, start_min = map(int, start_time_str.split(':'))
            end_hour, end_min = map(int, end_time_str.split(':'))
            start_time_obj = time(start_hour, start_min)
            end_time_obj = time(end_hour, end_min)
            
            # Insert meeting
            result = db.execute(
                text("""
                    INSERT INTO meetings (room_id, start_time, end_time)
                    VALUES (:room_id, :start_time, :end_time)
                    RETURNING meeting_id
                """),
                {
                    "room_id": room_id,
                    "start_time": start_time_obj,
                    "end_time": end_time_obj,
                }
            )
            meeting_id = result.fetchone()[0]
            
            # Insert employee_meetings
            for employee_id in employee_ids:
                db.execute(
                    text("""
                        INSERT INTO employee_meetings (employee_id, meeting_id)
                        VALUES (:employee_id, :meeting_id)
                    """),
                    {
                        "employee_id": employee_id,
                        "meeting_id": meeting_id,
                    }
                )
        
        db.commit()
        print("Meetings loaded successfully!")
    except Exception as e:
        print(f"Error loading meetings: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function to set up the database."""
    print("Starting database setup...")
    create_tables()
    load_rooms_from_csv()
    load_meetings_from_csv()
    print("Database setup complete!")


if __name__ == "__main__":
    main()
