from fastapi import APIRouter
from app.api.endpoints import tasks

api_router = APIRouter()

api_router.include_router(
    tasks.router,
    prefix='/tasks',
    tags=['tasks']
)

# We can add more routers here as we grow our API