from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.session import get_session
from app.schemas.book import BookCreate, BookUpdate, BookOut, BooksPage
from app.db import repo_books as repo
from app.services import books_service
from app.core.security import get_current_user
from app.core.rate_limits import rate_get, rate_mutate

router = APIRouter(prefix="/books", tags=["books"])


@router.post(
    "",
    response_model=BookOut,
    dependencies=[Depends(get_current_user)],
    summary="Create a new book",
    description="Add a new book record with title, author, genre, and published year.",
)
@rate_mutate
async def create_book(
    payload: BookCreate, session: AsyncSession = Depends(get_session)
):
    try:
        return await repo.create_book(
            session,
            title=payload.title,
            author=payload.author,
            genre=payload.genre,
            published_year=payload.published_year,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create book: {str(e)}")


@router.get(
    "",
    response_model=BooksPage,
    summary="List books",
    description="Retrieve all books with optional filters, pagination, and sorting.",
)
@rate_get
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
    data = await repo.list_books(
        session,
        title=title,
        author=author,
        genre=genre,
        year_from=year_from,
        year_to=year_to,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return {
        "items": data["items"],
        "total": data["total"],
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "sort_order": sort_order.lower(),
    }


@router.get(
    "/{book_id}",
    response_model=BookOut,
    summary="Get book by ID",
    description="Retrieve a single book by its unique identifier.",
)
@rate_get
async def get_book(book_id: int, session: AsyncSession = Depends(get_session)):
    book = await repo.get_book_by_id(session, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put(
    "/{book_id}",
    response_model=BookOut,
    dependencies=[Depends(get_current_user)],
    summary="Update a book",
    description="Update an existing book's details by its ID.",
)
@rate_mutate
async def update_book(
    book_id: int, payload: BookUpdate, session: AsyncSession = Depends(get_session)
):
    book = await repo.update_book(
        session,
        book_id,
        title=payload.title,
        author=payload.author,
        genre=payload.genre,
        published_year=payload.published_year,
    )
    if not book:
        raise HTTPException(status_code=404, detail="Book not found or not updated")
    return book


@router.delete(
    "/{book_id}",
    dependencies=[Depends(get_current_user)],
    summary="Delete a book",
    description="Remove a book record by its ID.",
)
@rate_mutate
async def delete_book(book_id: int, session: AsyncSession = Depends(get_session)):
    ok = await repo.delete_book(session, book_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"status": "deleted", "id": book_id}


@router.post(
    "/import",
    dependencies=[Depends(get_current_user)],
    summary="Import books",
    description="Bulk import books from JSON or CSV file.",
)
@rate_mutate
async def import_books(
    file: UploadFile = File(...), session: AsyncSession = Depends(get_session)
):
    return await books_service.import_books(file, session)


@router.get(
    "/export",
    summary="Export books",
    description="Export all books in JSON or CSV format.",
)
@rate_get
async def export_books(
    format: str = Query("json", regex="^(json|csv)$"),
    session: AsyncSession = Depends(get_session),
):
    return await books_service.export_books(format, session)


@router.get(
    "/recommendations",
    response_model=list[BookOut],
    summary="Get book recommendations",
    description="Recommend books based on genre or author.",
)
@rate_get
async def recommend_books(
    by: str = Query(..., regex="^(genre|author)$"),
    value: str = Query(...),
    limit: int = Query(5, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
):
    return await books_service.recommend_books(by, value, limit, session)
