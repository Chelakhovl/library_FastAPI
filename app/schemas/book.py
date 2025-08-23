from typing import Optional, Literal
from pydantic import BaseModel, field_validator
from datetime import datetime
from app.schemas.author import AuthorOut  # імпортуємо готову схему автора

# жанри як Enum через Literal
GenreLiteral = Literal["Fiction", "Non-Fiction", "Science", "History"]


# --- Base ---
class BookBase(BaseModel):
    title: str
    author: str   # ім'я автора (для створення книги)
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


# --- Create ---
class BookCreate(BookBase):
    pass


# --- Update ---
class BookUpdate(BaseModel):
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


# --- Out (response) ---
class BookOut(BaseModel):
    id: int
    title: str
    genre: GenreLiteral
    published_year: int
    created_at: datetime
    updated_at: datetime

    author_id: int
    author: AuthorOut  # вкладений об'єкт автора

    class Config:
        orm_mode = True


# --- Page for listing ---
class BooksPage(BaseModel):
    items: list[BookOut]
    total: int
    page: int
    page_size: int
    sort_by: str
    sort_order: str
