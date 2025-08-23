from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings
from app.db.session import engine, ping_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        ok = await ping_db()
        app.state.db_ready = bool(ok)
    except Exception:
        app.state.db_ready = False

    yield

    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api")