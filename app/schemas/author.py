from pydantic import BaseModel, field_validator
from datetime import datetime


# --- Base ---
class AuthorBase(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def non_empty_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("author name must be non-empty")
        return v


# --- Create ---
class AuthorCreate(AuthorBase):
    pass


# --- Update ---
class AuthorUpdate(AuthorBase):
    pass


# --- Out (response) ---
class AuthorOut(AuthorBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
