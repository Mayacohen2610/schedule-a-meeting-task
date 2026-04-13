"""
Setup script for test database.
Creates tables and optionally loads seed data in the test database.
"""
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Test database URL
TEST_DATABASE_URL = "postgresql://interview_user:interview_pass@localhost:5433/interview_db_test"


def create_tables():
    """Create all tables in test database."""
    from app.models import Base
    
    engine = create_engine(TEST_DATABASE_URL)
    
    print("Creating tables in test database...")
    try:
        # Drop existing tables and recreate
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("[OK] Tables created successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
        return False


def verify_setup():
    """Verify that test database is properly set up."""
    engine = create_engine(TEST_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # List all tables
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        
        print(f"\n[OK] Test database setup complete!")
        print(f"Tables created: {', '.join(tables)}")
        print(f"\nTest database: interview_db_test")
        print(f"Connection: {TEST_DATABASE_URL}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return False
    finally:
        db.close()


def main():
    """Main setup function."""
    print("=" * 60)
    print("Test Database Setup")
    print("=" * 60)
    
    # Check if test database exists
    try:
        engine = create_engine(TEST_DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("\n[OK] Test database exists (interview_db_test)")
    except Exception as e:
        print(f"\n[ERROR] Cannot connect to test database: {e}")
        print("\nPlease create the test database first:")
        print("  docker exec interview_template_postgres psql -U interview_user -d interview_db -c \"CREATE DATABASE interview_db_test;\"")
        return 1
    
    # Create tables
    print("\n" + "-" * 60)
    if not create_tables():
        return 1
    
    # Verify setup
    print("\n" + "-" * 60)
    if not verify_setup():
        return 1
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Test database is ready!")
    print("=" * 60)
    print("\nYou can now run tests with:")
    print("  python tests/run_tests.py")
    print("  or")
    print("  .\\venv\\Scripts\\python.exe -m pytest tests/ -v")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
