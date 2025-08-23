from pydantic import BaseModel, EmailStr, constr
from datetime import datetime


class UserBase(BaseModel):
    """
    Base schema for users.
    Contains common fields shared across other schemas.
    """

    email: EmailStr


class UserCreate(UserBase):
    """
    Schema for user registration.
    Requires a valid email and password (min length 6).
    """

    password: constr(min_length=6)


class UserLogin(UserBase):
    """
    Schema for user authentication (login).
    """

    password: str


class UserOut(UserBase):
    """
    Schema for returning user details in API responses.
    Excludes password for security reasons.
    """

    id: int
    created_at: datetime

    class Config:
        from_attributes = True
