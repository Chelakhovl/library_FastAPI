from typing import Optional, Literal
from pydantic import BaseModel, field_validator
from datetime import datetime
from app.schemas.author import AuthorOut

GenreLiteral = Literal["Fiction", "Non-Fiction", "Science", "History"]


class BookBase(BaseModel):
    """
    Base schema for books.
    Defines shared fields and validation.
    """

    title: str
    author: str
    genre: GenreLiteral
    published_year: int

    @field_validator("title")
    @classmethod
    def non_empty_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title must be non-empty")
        return v

    @field_validator("author")
    @classmethod
    def non_empty_author(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("author must be non-empty")
        return v

    @field_validator("published_year")
    @classmethod
    def valid_year(cls, v: int) -> int:
        year_now = datetime.now().year
        if v < 1800 or v > year_now:
            raise ValueError(f"published_year must be between 1800 and {year_now}")
        return v


class BookCreate(BookBase):
    """
    Schema for creating a new book.
    """

    pass


class BookUpdate(BaseModel):
    """
    Schema for updating an existing book.
    All fields are optional.
    """

    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[GenreLiteral] = None
    published_year: Optional[int] = None

    @field_validator("title")
    @classmethod
    def non_empty_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("title must be non-empty")
        return v

    @field_validator("author")
    @classmethod
    def non_empty_author(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("author must be non-empty")
        return v

    @field_validator("published_year")
    @classmethod
    def valid_year(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        year_now = datetime.now().year
        if v < 1800 or v > year_now:
            raise ValueError(f"published_year must be between 1800 and {year_now}")
        return v


class BookOut(BaseModel):
    """
    Schema for returning book details in API responses.
    Includes nested author info.
    """

    id: int
    title: str
    genre: GenreLiteral
    published_year: int
    created_at: datetime
    updated_at: datetime
    author_id: int
    author: AuthorOut

    class Config:
        orm_mode = True


class BooksPage(BaseModel):
    """
    Schema for paginated book listings.
    """

    items: list[BookOut]
    total: int
    page: int
    page_size: int
    sort_by: str
    sort_order: str
