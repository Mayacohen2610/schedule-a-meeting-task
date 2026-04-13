"""
Pytest configuration and shared fixtures.
Ensures clean test data and proper database state.
Uses a separate test database to avoid affecting production data.
"""
import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Use separate test database to ensure complete isolation
# This prevents tests from affecting production data
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://interview_user:interview_pass@localhost:5433/interview_db_test"
)


@pytest.fixture(scope="session")
def engine():
    """
    Create a test database engine.
    Uses interview_db_test to ensure complete isolation from production data.
    """
    return create_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="function")
def db_session(engine):
    """
    Create a database session for testing.
    Cleans up test data after each test.
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    yield db
    
    # Cleanup: Remove all test data (we can be more aggressive since this is a test DB)
    try:
        db.execute(text("TRUNCATE employee_meetings CASCADE"))
        db.execute(text("DELETE FROM meetings"))
        db.execute(text("DELETE FROM employees"))
        db.execute(text("DELETE FROM rooms"))
        db.execute(text("DELETE FROM items"))
        db.commit()
    except Exception as e:
        print(f"Cleanup error: {e}")
        db.rollback()
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database(engine):
    """
    Set up the test database schema before running tests.
    Runs once at the start of the test session.
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Import models to ensure tables are created
        from app.models import Base
        
        # Drop all tables and recreate (clean slate for tests)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        print("\n[OK] Test database schema initialized")
        
        # Optionally: Load minimal seed data needed for tests
        # For now, tests will create their own data
        
    except Exception as e:
        print(f"\nWarning: Test database setup failed: {e}")
        db.rollback()
    finally:
        db.close()
    
    yield
    
    # Optional: Clean up after all tests
    print("\n[OK] Test session completed")


@pytest.fixture(scope="function")
def clean_test_meetings(db_session):
    """
    Fixture that cleans up meetings created during auto-schedule tests.
    Use this fixture for tests that create meetings with existing employees.
    """
    created_meeting_ids = []
    
    def track_meeting(meeting_id):
        """Track a meeting ID for cleanup."""
        created_meeting_ids.append(meeting_id)
    
    yield track_meeting
    
    # Cleanup all tracked meetings
    for meeting_id in created_meeting_ids:
        try:
            db_session.execute(
                text("DELETE FROM employee_meetings WHERE meeting_id = :meeting_id"),
                {"meeting_id": meeting_id}
            )
            db_session.execute(
                text("DELETE FROM meetings WHERE meeting_id = :meeting_id"),
                {"meeting_id": meeting_id}
            )
            db_session.commit()
        except Exception:
            db_session.rollback()
