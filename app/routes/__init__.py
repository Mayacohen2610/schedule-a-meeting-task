"""
API routes module.
Exports all routers from individual entity modules.
"""
from fastapi import APIRouter

from app.routes.items import router as items_router
from app.routes.employees import router as employees_router
from app.routes.rooms import router as rooms_router
from app.routes.meetings import router as meetings_router
from app.routes.health import router as health_router

# Main router that includes all sub-routers
router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(items_router, tags=["items"])
router.include_router(employees_router, tags=["employees"])
router.include_router(rooms_router, tags=["rooms"])
router.include_router(meetings_router, tags=["meetings"])

__all__ = ["router"]
