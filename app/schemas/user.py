from pydantic import BaseModel, EmailStr, constr
from datetime import datetime


# --- Base ---
class UserBase(BaseModel):
    email: EmailStr


# --- Create (реєстрація) ---
class UserCreate(UserBase):
    password: constr(min_length=6)


# --- Login (автентифікація) ---
class UserLogin(UserBase):
    password: str


# --- Out (відповідь) ---
class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
