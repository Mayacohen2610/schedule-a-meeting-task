# Code Structure

Overview of the modular code organization.

## Project Structure

```
schedule-a-meeting-task/
├── app/
│   ├── crud/              # Business logic (6 files)
│   │   ├── items.py       # Items operations
│   │   ├── employees.py   # Employees operations
│   │   ├── rooms.py       # Rooms operations
│   │   ├── meetings.py    # Meetings operations
│   │   └── utils.py       # Shared utilities
│   ├── routes/            # API endpoints (6 files)
│   │   ├── items.py       # Items endpoints
│   │   ├── employees.py   # Employees endpoints
│   │   ├── rooms.py       # Rooms endpoints
│   │   ├── meetings.py    # Meetings endpoints
│   │   └── health.py      # Health check
│   ├── main.py            # FastAPI app
│   ├── database.py        # DB connection
│   ├── schemas.py         # Validation
│   └── models.py          # ORM models
├── tests/                 # 109 tests
├── docs/                  # Documentation
└── scripts/               # Setup scripts
```

## Why Modular?

### Before (Monolithic)
- `crud.py` - 620 lines, all logic in one file
- `routes.py` - 184 lines, all endpoints in one file
- Hard to find specific code
- Difficult to maintain

### After (Modular)
- Each entity has its own file
- Average file size: ~70 lines
- Easy to find and modify
- Clear organization

## Benefits

✅ **Easy to navigate** - Find code by entity name
✅ **Simple to maintain** - Each file has single purpose
✅ **Scalable** - Add new entities without touching existing code
✅ **Better testing** - Test modules independently
✅ **Team-friendly** - Multiple developers can work in parallel

## Adding New Entity

Example: Add "Projects" entity

1. **Create CRUD file**: `app/crud/projects.py`
2. **Create routes file**: `app/routes/projects.py`  
3. **Export in** `app/crud/__init__.py`
4. **Register router in** `app/routes/__init__.py`

Done! The new entity is fully integrated.

## Backward Compatible

All existing imports still work:
```python
from app import crud
crud.get_all_items(db)      # ✅ Works
crud.create_meeting(db, m)  # ✅ Works
```

The `__init__.py` files export everything automatically.
