import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app.main import app
from app.db import Base, get_db
from app.core.config import settings


TEST_DB_URL = settings.TEST_DB_URL

sync_engine = create_engine(TEST_DB_URL.replace("+asyncpg", ""))

engine_test = create_async_engine(
    TEST_DB_URL,
    future=True,
    echo=False,
    poolclass=NullPool,
)
TestingSessionLocal = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    """Create tables once before running all tests."""
    Base.metadata.drop_all(bind=sync_engine)
    Base.metadata.create_all(bind=sync_engine)
    yield
    Base.metadata.drop_all(bind=sync_engine)


@pytest.fixture(autouse=True)
async def clean_database():
    """Truncate all tables before each test and dispose connections."""
    async with engine_test.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    await engine_test.dispose()
    yield


async def override_get_db():
    """Provide a test database session with rollback on failure."""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client():
    """Return an HTTPX client for FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_token(client):
    """Generate a valid JWT token for a unique test user."""
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    await client.post(
        "/api/auth/register", json={"email": email, "password": "password123"}
    )
    resp = await client.post(
        "/api/auth/login", json={"email": email, "password": "password123"}
    )
    return resp.json()["access_token"]
