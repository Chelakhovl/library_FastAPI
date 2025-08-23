from fastapi import APIRouter
from . import health
from . import books
from . import auth

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(books.router)
api_router.include_router(auth.router)
