from fastapi import APIRouter
from app.db.session import ping_db

router = APIRouter()


@router.get("/health", summary="App health check")
async def health():
    return {"status": "ok"}


@router.get("/health/db", summary="Database health check")
async def health_db():
    ok = await ping_db()
    return {"db": "ok" if ok else "down"}
