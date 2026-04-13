"""
Pytest tests for API endpoints using FastAPI TestClient.
"""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_endpoint():
    """Tests the /health endpoint returns status up or down."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ("up", "down")


def test_get_items_returns_list():
    """Tests the GET /items endpoint returns a list."""
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_items_structure():
    """Tests that each item in GET /items has the expected fields."""
    response = client.get("/items")
    assert response.status_code == 200
    items = response.json()
    for item in items:
        assert "id" in item
        assert "item_name" in item
        assert "category" in item
        assert "price" in item
        assert "in_stock" in item


def test_post_item_and_get():
    """Tests creating an item via POST /items and fetching it via GET /items."""
    new_item = {
        "item_name": "Test Item",
        "category": "Test Category",
        "price": 9.99,
        "in_stock": True,
    }
    response = client.post("/items", json=new_item)
    assert response.status_code == 200
    created = response.json()
    assert created["item_name"] == new_item["item_name"]
    assert created["category"] == new_item["category"]
    assert created["price"] == new_item["price"]
    assert created["in_stock"] == new_item["in_stock"]
    assert "id" in created