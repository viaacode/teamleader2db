from fastapi import APIRouter

from app.api.routers import sync, health

api_router = APIRouter()

api_router.include_router(
    sync.router,
    prefix="/sync",
    tags=["Synchronize Teamleader data to database"]
)

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health check"]
)
