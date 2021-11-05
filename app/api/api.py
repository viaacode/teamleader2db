from fastapi import APIRouter

from app.api.routers import sync, health, export

api_router = APIRouter()

api_router.include_router(
    sync.router,
    prefix="/sync",
    tags=["Synchronize Teamleader data to database"]
)

api_router.include_router(
    export.router,
    prefix="/export",
    tags=["Export Teamleader data to csv file"]
)

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health check"]
)
