"""
Creates the 'items' table in the fiverr_db PostgreSQL database.
Run this script once to set up the table before using the item endpoints.
"""
from sqlalchemy import text

from app.database import engine

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            item_name VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL,
            price DOUBLE PRECISION NOT NULL,
            in_stock BOOLEAN DEFAULT TRUE
        )
    """))
    conn.commit()
    print("Items table created successfully!")