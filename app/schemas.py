"""
Pydantic schemas for request/response validation.
"""
from typing import Optional

from pydantic import BaseModel


class ItemCreate(BaseModel):
    """Request body for creating a new item."""

    item_name: str
    category: str
    price: float
    in_stock: bool = True


class ItemUpdate(BaseModel):
    """Request body for partial update of an item. All fields are optional."""

    price: Optional[float] = None
    in_stock: Optional[bool] = None


class ItemResponse(BaseModel):
    """Response schema for an item."""

    id: int
    item_name: str
    category: str
    price: float
    in_stock: bool