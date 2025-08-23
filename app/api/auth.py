from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_session
from app.core.security import get_password_hash, verify_password, create_access_token
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/register", status_code=201)
async def register(email: str = Form(...), password: str = Form(...), session: AsyncSession = Depends(get_session)):
    hashed = get_password_hash(password)
    try:
        q = text("INSERT INTO users(email, hashed_password) VALUES(:e, :p)")
        await session.execute(q, {"e": email.strip(), "p": hashed})
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Cannot register: {e}")
    return {"status": "ok"}

@router.post("/login", response_model=TokenOut)
async def login(email: str = Form(...), password: str = Form(...), session: AsyncSession = Depends(get_session)):
    q = text("SELECT id, hashed_password FROM users WHERE email = :e")
    row = (await session.execute(q, {"e": email.strip()})).first()
    if not row or not verify_password(password, row.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(row.id), "email": email})
    return TokenOut(access_token=token)