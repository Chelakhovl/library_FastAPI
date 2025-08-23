from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain password against its hashed version.
    """
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_minutes: int = 60) -> str:
    """
    Create a signed JWT access token.

    Args:
        data (dict): Claims to include in the token.
        expires_minutes (int): Token expiration time in minutes.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


class TokenData(BaseModel):
    """
    Token payload model extracted from JWT.
    """

    user_id: int
    email: str


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> TokenData:
    """
    Validate JWT token and fetch the current user.

    Args:
        token (str): Bearer token from the Authorization header.
        session (AsyncSession): Active database session.

    Returns:
        TokenData: Decoded token data containing user_id and email.

    Raises:
        HTTPException: 401 if token is invalid or user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        user_id = int(payload.get("sub"))
        email = payload.get("email")
        if not user_id or not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    res = await session.execute(
        text("SELECT id, email FROM users WHERE id = :id"), {"id": user_id}
    )
    row = res.first()
    if not row:
        raise credentials_exception
    return TokenData(user_id=user_id, email=email)
