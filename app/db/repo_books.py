from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.constants import ALLOWED_SORT_FIELDS


def _sort_clause(sort_by: str, sort_order: str) -> str:
    """
    Build a safe ORDER BY clause for book queries.

    Args:
        sort_by (str): The field to sort by ("title", "author", "published_year").
        sort_order (str): The sort direction ("asc" or "desc").

    Returns:
        str: SQL ORDER BY clause.
    """
    sb = sort_by if sort_by in ALLOWED_SORT_FIELDS else "title"
    so = "DESC" if sort_order.lower() == "desc" else "ASC"
    if sb == "author":
        return f"ORDER BY a.name {so}, b.id ASC"
    if sb == "published_year":
        return f"ORDER BY b.published_year {so}, b.id ASC"
    return f"ORDER BY b.title {so}, b.id ASC"


async def create_book(
    session: AsyncSession,
    *,
    title: str,
    author: str,
    genre: str,
    published_year: int,
) -> dict:
    """
    Create a new book record. Automatically inserts or fetches the author.

    Returns:
        dict: Created book record.
    """
    q = text("SELECT author_get_or_create(:author) AS author_id")
    res = await session.execute(q, {"author": author})
    author_id = res.scalar_one()

    q2 = text(
        """
        INSERT INTO books(title, author_id, genre, published_year)
        VALUES (:title, :author_id, :genre, :year)
        RETURNING id, title, :author as author, genre, published_year,
                  created_at::text, updated_at::text
    """
    )
    row = (
        (
            await session.execute(
                q2,
                {
                    "title": title,
                    "author_id": author_id,
                    "genre": genre,
                    "year": published_year,
                    "author": author,
                },
            )
        )
        .mappings()
        .one()
    )
    await session.commit()
    return dict(row)


async def get_book_by_id(session: AsyncSession, book_id: int) -> Optional[dict]:
    """
    Fetch a book by its ID.

    Returns:
        dict: Book record, or None if not found.
    """
    q = text(
        """
        SELECT b.id, b.title, a.name AS author, b.genre, b.published_year,
               b.created_at::text, b.updated_at::text
        FROM books b
        JOIN authors a ON a.id = b.author_id
        WHERE b.id = :id
    """
    )
    res = await session.execute(q, {"id": book_id})
    row = res.mappings().first()
    return dict(row) if row else None


async def delete_book(session: AsyncSession, book_id: int) -> bool:
    """
    Delete a book by its ID.

    Returns:
        bool: True if deleted, False if not found.
    """
    q = text("DELETE FROM books WHERE id = :id")
    res = await session.execute(q, {"id": book_id})
    await session.commit()
    return res.rowcount > 0


async def update_book(
    session: AsyncSession,
    book_id: int,
    *,
    title: Optional[str],
    author: Optional[str],
    genre: Optional[str],
    published_year: Optional[int],
) -> Optional[dict]:
    """
    Update book details. Supports partial updates.
    If no fields provided, returns the current book record.

    Returns:
        dict: Updated book record, or None if not found.
    """
    author_id = None
    if author is not None:
        res = await session.execute(
            text("SELECT author_get_or_create(:a) AS author_id"), {"a": author}
        )
        author_id = res.scalar_one()

    sets = []
    params = {"id": book_id}
    if title is not None:
        sets.append("title = :title")
        params["title"] = title
    if author_id is not None:
        sets.append("author_id = :author_id")
        params["author_id"] = author_id
    if genre is not None:
        sets.append("genre = :genre")
        params["genre"] = genre
    if published_year is not None:
        sets.append("published_year = :year")
        params["year"] = published_year

    if not sets:
        return await get_book_by_id(session, book_id)

    q = text(
        f"""
        UPDATE books
        SET {", ".join(sets)}, updated_at = NOW()
        WHERE id = :id
        RETURNING id
    """
    )
    res = await session.execute(q, params)
    if res.rowcount == 0:
        await session.rollback()
        return None
    await session.commit()
    return await get_book_by_id(session, book_id)


async def list_books(
    session: AsyncSession,
    *,
    title: Optional[str],
    author: Optional[str],
    genre: Optional[str],
    year_from: Optional[int],
    year_to: Optional[int],
    page: int,
    page_size: int,
    sort_by: str,
    sort_order: str,
) -> dict:
    """
    List books with filters, pagination, and sorting.

    Args:
        title (str, optional): Filter by title (LIKE).
        author (str, optional): Filter by author name (LIKE).
        genre (str, optional): Filter by genre.
        year_from (int, optional): Minimum published year.
        year_to (int, optional): Maximum published year.
        page (int): Page number.
        page_size (int): Number of records per page.
        sort_by (str): Sort field.
        sort_order (str): Sort direction.

    Returns:
        dict: {
            "items": [list of book dicts],
            "total": total_count
        }
    """
    filters = []
    params = {}
    if title:
        filters.append("lower(b.title) LIKE lower(:title)")
        params["title"] = f"%{title}%"
    if author:
        filters.append("lower(a.name) LIKE lower(:author)")
        params["author"] = f"%{author}%"
    if genre:
        filters.append("b.genre = :genre")
        params["genre"] = genre
    if year_from is not None:
        filters.append("b.published_year >= :yfrom")
        params["yfrom"] = year_from
    if year_to is not None:
        filters.append("b.published_year <= :yto")
        params["yto"] = year_to

    where = ("WHERE " + " AND ".join(filters)) if filters else ""
    order_clause = _sort_clause(sort_by, sort_order)
    limit_offset = "LIMIT :limit OFFSET :offset"
    params.update({"limit": page_size, "offset": (page - 1) * page_size})

    q_items = text(
        f"""
        SELECT b.id, b.title, a.name AS author, b.genre, b.published_year,
               b.created_at::text, b.updated_at::text
        FROM books b
        JOIN authors a ON a.id = b.author_id
        {where}
        {order_clause}
        {limit_offset}
    """
    )
    rows = (await session.execute(q_items, params)).mappings().all()

    q_count = text(
        f"""
        SELECT COUNT(*) FROM books b
        JOIN authors a ON a.id = b.author_id
        {where}
    """
    )
    total = (await session.execute(q_count, params)).scalar_one()
    return {"items": [dict(r) for r in rows], "total": int(total)}
