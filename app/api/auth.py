from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_session
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_user
from app.schemas.user import UserCreate, UserLogin, UserOut
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", status_code=201, response_model=UserOut)
async def register(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    hashed = get_password_hash(payload.password)
    try:
        q = text(
            "INSERT INTO users(email, hashed_password) VALUES(:e, :p) RETURNING id, email, created_at"
        )
        row = (await session.execute(q, {"e": payload.email.strip(), "p": hashed})).first()
        await session.commit()
        return UserOut(id=row.id, email=row.email, created_at=row.created_at)
    except Exception as e:
        await session.rollback()
        # якщо дублюється email → 409 Conflict
        raise HTTPException(status_code=409, detail="Email already registered")


@router.post("/login", response_model=TokenOut)
async def login(payload: UserLogin, session: AsyncSession = Depends(get_session)):
    q = text("SELECT id, hashed_password FROM users WHERE email = :e")
    row = (await session.execute(q, {"e": payload.email.strip()})).first()
    if not row or not verify_password(payload.password, row.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token = create_access_token({"sub": str(row.id), "email": payload.email})
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(current_user: UserOut = Depends(get_current_user)):
    return current_user
