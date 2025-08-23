# app/api/books.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.session import get_session
from app.schemas.book import BookCreate, BookUpdate, BookOut, BooksPage
from app.db import repo_books as repo
from app.core.constants import GENRES
from app.core.security import get_current_user
import csv, io, json

router = APIRouter(prefix="/books", tags=["books"])

@router.post("", response_model=BookOut, dependencies=[Depends(get_current_user)])
async def create_book(payload: BookCreate, session: AsyncSession = Depends(get_session)):
    try:
        book = await repo.create_book(session,
            title=payload.title, author=payload.author,
            genre=payload.genre, published_year=payload.published_year)
        return book
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create book: {str(e)}")

@router.get("", response_model=BooksPage)
async def list_books(
    session: AsyncSession = Depends(get_session),
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    year_from: Optional[int] = Query(None, ge=1800),
    year_to: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("title"),
    sort_order: str = Query("asc"),
):
    data = await repo.list_books(session,
        title=title, author=author, genre=genre,
        year_from=year_from, year_to=year_to,
        page=page, page_size=page_size,
        sort_by=sort_by, sort_order=sort_order
    )
    return {
        "items": data["items"],
        "total": data["total"],
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "sort_order": sort_order.lower(),
    }

@router.get("/{book_id}", response_model=BookOut)
async def get_book(book_id: int, session: AsyncSession = Depends(get_session)):
    book = await repo.get_book_by_id(session, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{book_id}", response_model=BookOut, dependencies=[Depends(get_current_user)])
async def update_book(book_id: int, payload: BookUpdate, session: AsyncSession = Depends(get_session)):
    book = await repo.update_book(session, book_id,
        title=payload.title, author=payload.author, genre=payload.genre, published_year=payload.published_year)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found or not updated")
    return book

@router.delete("/{book_id}", dependencies=[Depends(get_current_user)])
async def delete_book(book_id: int, session: AsyncSession = Depends(get_session)):
    ok = await repo.delete_book(session, book_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"status": "deleted", "id": book_id}

@router.post("/import", dependencies=[Depends(get_current_user)])
async def import_books(file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    """
    Підтримує:
    - JSON: масив об'єктів {title, author, genre, published_year}
    - CSV: заголовки title,author,genre,published_year
    """
    content = await file.read()
    created = 0
    errors = []

    def record_ok(rec: dict) -> bool:
        base_keys = {"title","author","genre","published_year"}
        if not base_keys.issubset(rec.keys()):
            return False
        if rec["genre"] not in GENRES:
            return False
        try:
            y = int(rec["published_year"])
            if y < 1800: return False
        except: return False
        return True

    try:
        if file.filename.endswith(".json"):
            data = json.loads(content.decode("utf-8"))
            if not isinstance(data, list):
                raise ValueError("JSON must be an array of records")
            for i, rec in enumerate(data, 1):
                if not record_ok(rec):
                    errors.append(f"row {i}: invalid record")
                    continue
                try:
                    await repo.create_book(session, title=rec["title"], author=rec["author"],
                                           genre=rec["genre"], published_year=int(rec["published_year"]))
                    created += 1
                except Exception as e:
                    errors.append(f"row {i}: {e}")
        else:
            # CSV
            reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
            for i, rec in enumerate(reader, 1):
                if not record_ok(rec):
                    errors.append(f"row {i}: invalid record")
                    continue
                try:
                    await repo.create_book(session, title=rec["title"], author=rec["author"],
                                           genre=rec["genre"], published_year=int(rec["published_year"]))
                    created += 1
                except Exception as e:
                    errors.append(f"row {i}: {e}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

    return {"imported": created, "errors": errors}
