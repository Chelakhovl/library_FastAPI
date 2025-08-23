from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded

from app.api.router import api_router
from app.core.config import settings
from app.db.session import engine, ping_db
from app.core.errors import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
    rate_limit_handler,
)
from app.core.limiter import limiter


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

app.state.limiter = limiter


app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

app.include_router(api_router, prefix="/api")
