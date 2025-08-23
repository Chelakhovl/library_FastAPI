from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.db import repo_users as repo
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.schemas.user import UserCreate, UserLogin, UserOut
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post(
    "/register",
    status_code=201,
    response_model=UserOut,
    summary="Register a new user",
    description="Create a new user account with an email and password.",
)
async def register(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    hashed = get_password_hash(payload.password)
    try:
        row = await repo.create_user(session, payload.email.strip(), hashed)
        await session.commit()
        return UserOut(id=row.id, email=row.email, created_at=row.created_at)
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="User with this email already exists"
        )


@router.post(
    "/login",
    response_model=TokenOut,
    summary="User login",
    description="Authenticate user with email and password, returns a JWT token.",
)
async def login(payload: UserLogin, session: AsyncSession = Depends(get_session)):
    row = await repo.get_user_by_email(session, payload.email.strip())
    if not row or not verify_password(payload.password, row.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token = create_access_token({"sub": str(row.id), "email": payload.email})
    return TokenOut(access_token=token)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user",
    description="Return details of the currently authenticated user.",
)
async def me(current_user: UserOut = Depends(get_current_user)):
    return current_user
