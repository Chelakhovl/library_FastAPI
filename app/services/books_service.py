import csv, io, json
from fastapi import UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import select
from datetime import datetime
from app.db.book import Book
from app.db.author import Author
from app.schemas.book import BookOut
from app.db import repo_books as repo
from app.core.constants import GENRES


def record_ok(rec: dict) -> bool:
    """
    Validate a single book record.

    Ensures required fields exist, genre is valid,
    and published_year is an integer >= 1800.
    """
    base_keys = {"title", "author", "genre", "published_year"}
    if not base_keys.issubset(rec.keys()):
        return False
    if rec["genre"] not in GENRES:
        return False
    try:
        y = int(rec["published_year"])
        if y < 1800:
            return False
    except Exception:
        return False
    return True


async def import_books(file: UploadFile, session):
    """
    Import books from a JSON or CSV file.

    - JSON: expects an array of objects {title, author, genre, published_year}
    - CSV: expects headers [title, author, genre, published_year]

    Returns:
        dict: {
            "imported": <number of successfully imported books>,
            "errors": [list of error messages per row]
        }
    """
    content = await file.read()
    created, errors = 0, []

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
                    await repo.create_book(
                    session,
                    title=rec["title"],
                    author=rec["author"],
                    genre=rec["genre"],
                    published_year=int(rec["published_year"]),
                )
                    created += 1
                except Exception as e:
                    errors.append(f"row {i}: {e}")
        else:
            reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
            for i, rec in enumerate(reader, 1):
                if not record_ok(rec):
                    errors.append(f"row {i}: invalid record")
                    continue
                try:
                    await repo.create_book(
                        session,
                        title=rec["title"],
                        author=rec["author"],
                        genre=rec["genre"],
                        published_year=int(rec["published_year"]),
                    )
                    created += 1
                except Exception as e:
                    errors.append(f"row {i}: {e}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

    return {"imported": created, "errors": errors}


async def export_books(format: str, session):
    """
    Export books in JSON or CSV format.

    Args:
        format (str): "json" or "csv"
        session (AsyncSession): database session

    Returns:
        - JSONResponse with book list if format=json
        - StreamingResponse with CSV file if format=csv
    """
    result = await session.execute(
        select(
            Book.id,
            Book.title,
            Book.genre,
            Book.published_year,
            Author.name.label("author"),
        ).join(Author, Book.author_id == Author.id)
    )
    books = result.mappings().all()

    if format == "json":
        return JSONResponse(content=[dict(row) for row in books])
    else:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["title", "author", "genre", "published_year"])
        for row in books:
            writer.writerow([row.title, row.author, row.genre, row.published_year])
        output.seek(0)
        filename = f"books_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )


async def recommend_books(by: str, value: str, limit: int, session):
    """
    Recommend books based on genre or author.
    """
    if by == "genre":
        query = (
            select(
                Book.id,
                Book.title,
                Book.genre,
                Book.published_year,
                Author.id.label("author_id"),
                Author.name.label("author"),
                Book.created_at,
                Book.updated_at,
            )
            .join(Author, Book.author_id == Author.id)
            .where(Book.genre == value)
            .limit(limit)
        )
    else:
        query = (
            select(
                Book.id,
                Book.title,
                Book.genre,
                Book.published_year,
                Author.id.label("author_id"),
                Author.name.label("author"),
                Book.created_at,
                Book.updated_at,
            )
            .join(Author, Book.author_id == Author.id)
            .where(Author.name.ilike(f"%{value}%"))
            .limit(limit)
        )

    result = await session.execute(query)
    rows = result.mappings().all()

    if not rows:
        raise HTTPException(status_code=404, detail="No recommendations found")

    return [BookOut(**dict(r)) for r in rows]
