from pydantic import BaseModel, field_validator
from datetime import datetime


class AuthorBase(BaseModel):
    """
    Base schema for authors.
    Used for shared fields between create, update, and output.
    """

    name: str

    @field_validator("name")
    @classmethod
    def non_empty_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Author name must be non-empty")
        return v


class AuthorCreate(AuthorBase):
    """
    Schema for creating a new author.
    """

    pass


class AuthorUpdate(AuthorBase):
    """
    Schema for updating an existing author.
    """

    pass


class AuthorOut(AuthorBase):
    """
    Schema for returning author details in API responses.
    """

    id: int
    created_at: datetime

    class Config:
        from_attributes = True
