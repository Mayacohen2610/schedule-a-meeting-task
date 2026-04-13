"""
Test runner script with database cleanup.
Ensures clean test data before and after running tests.
Uses separate test database (interview_db_test) to protect production data.
"""
import sys
from pathlib import Path

# Add parent directory to Python path so we can import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Use test database URL
TEST_DATABASE_URL = "postgresql://interview_user:interview_pass@localhost:5433/interview_db_test"


def cleanup_test_data():
    """Remove all test data from test database."""
    engine = create_engine(TEST_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Cleaning up test database...")
        
        # Truncate all tables in test database
        db.execute(text("TRUNCATE employee_meetings CASCADE"))
        db.execute(text("DELETE FROM meetings"))
        db.execute(text("DELETE FROM employees"))
        db.execute(text("DELETE FROM rooms"))
        db.execute(text("DELETE FROM items"))
        db.commit()
        
        print("[OK] Test database cleaned successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Cleanup failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def verify_test_database():
    """Verify that test database exists and has required tables."""
    engine = create_engine(TEST_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if tables exist
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """))
        tables = [row[0] for row in result.fetchall()]
        
        required_tables = ['employees', 'rooms', 'meetings', 'employee_meetings', 'items']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"\n[WARNING] Test database is missing tables: {', '.join(missing_tables)}")
            print("Run the setup script to initialize test database:")
            print("  python tests/setup_test_db.py")
            return False
        
        print(f"\n[OK] Test database verified ({len(tables)} tables)")
        return True
    except Exception as e:
        print(f"[ERROR] Database verification failed: {e}")
        print("Make sure test database exists:")
        print("  docker exec interview_template_postgres psql -U interview_user -d interview_db -c \"CREATE DATABASE interview_db_test;\"")
        return False
    finally:
        db.close()


def main():
    """Main test runner."""
    print("=" * 60)
    print("Meeting Scheduling Service - Test Runner")
    print("Using Test Database: interview_db_test")
    print("=" * 60)
    
    # Verify test database exists
    print("\n1. Verifying test database...")
    if not verify_test_database():
        print("\n[ERROR] Test database not properly set up. Exiting.")
        return 1
    
    # Cleanup before tests
    print("\n2. Pre-test cleanup...")
    if not cleanup_test_data():
        print("\n[WARNING] Cleanup failed but continuing with tests...")
    
    # Run tests
    print("\n3. Running tests...")
    print("=" * 60)
    
    import pytest
    exit_code = pytest.main([
        "-v",
        "--tb=short",
        "-ra",
        "tests/"
    ])
    
    # Cleanup after tests
    print("\n" + "=" * 60)
    print("4. Post-test cleanup...")
    cleanup_test_data()
    
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("[SUCCESS] All tests passed!")
    else:
        print(f"[FAILURE] Tests failed with exit code: {exit_code}")
    print("=" * 60)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
