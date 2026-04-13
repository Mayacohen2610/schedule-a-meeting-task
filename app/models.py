"""
SQLAlchemy models and table definitions.
"""
from sqlalchemy import Boolean, Column, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Item(Base):
    """ORM model for the items table."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)