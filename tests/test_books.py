import pytest


@pytest.mark.asyncio
async def test_create_book_success(client, auth_token):
    """
    Create a book with valid data.
    Expect: 200 OK, response contains correct title, author, and genre.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}

    resp = await client.post(
        "/api/books",
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "genre": "Science",
            "published_year": 2008,
        },
        headers=headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Clean Code"
    assert data["author"] == "Robert C. Martin"
    assert data["genre"] == "Science"


@pytest.mark.asyncio
async def test_create_book_invalid_data(client, auth_token):
    """
    Attempt to create a book with invalid data (year too old).
    Expect: 400 or 422 error.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = await client.post(
        "/api/books",
        json={
            "title": "Ancient Book",
            "author": "Unknown",
            "genre": "Fiction",
            "published_year": 1500,
        },
        headers=headers,
    )

    assert resp.status_code in (400, 422)
    data = resp.json()
    assert "error" in data or "detail" in data


@pytest.mark.asyncio
async def test_create_book_unauthorized(client):
    """
    Attempt to create a book without an auth token.
    Expect: 401 Unauthorized.
    """
    resp = await client.post(
        "/api/books",
        json={
            "title": "No Auth Book",
            "author": "Hacker",
            "genre": "History",
            "published_year": 1999,
        },
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_book_by_id(client, auth_token):
    """
    Create a book and retrieve it by ID.
    Expect: 200 OK, response contains correct title.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = await client.post(
        "/api/books",
        json={
            "title": "Domain-Driven Design",
            "author": "Eric Evans",
            "genre": "Science",
            "published_year": 2003,
        },
        headers=headers,
    )
    book_id = resp.json()["id"]

    resp = await client.get(f"/api/books/{book_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Domain-Driven Design"


@pytest.mark.asyncio
async def test_get_book_not_found(client):
    """
    Retrieve a non-existent book by ID.
    Expect: 404 Not Found.
    """
    resp = await client.get("/api/books/99999")
    assert resp.status_code == 404
    data = resp.json()
    assert data["error"]["code"] == 404


@pytest.mark.asyncio
async def test_list_books_with_filters(client, auth_token):
    """
    List books with filtering by genre.
    Expect: returned items contain only matching genre.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    await client.post(
        "/api/books",
        json={
            "title": "Book A",
            "author": "Author1",
            "genre": "Fiction",
            "published_year": 1999,
        },
        headers=headers,
    )
    await client.post(
        "/api/books",
        json={
            "title": "Book B",
            "author": "Author2",
            "genre": "History",
            "published_year": 2010,
        },
        headers=headers,
    )

    resp = await client.get("/api/books?genre=Fiction&page=1&page_size=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert all(item["genre"] == "Fiction" for item in data["items"])


@pytest.mark.asyncio
async def test_update_book_success(client, auth_token):
    """
    Create a book, update its details, and verify the changes.
    Expect: 200 OK, updated fields returned.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = await client.post(
        "/api/books",
        json={
            "title": "Old Title",
            "author": "Unknown",
            "genre": "Fiction",
            "published_year": 2000,
        },
        headers=headers,
    )
    book_id = resp.json()["id"]

    resp = await client.put(
        f"/api/books/{book_id}",
        json={
            "title": "New Title",
            "author": "Updated Author",
            "genre": "Non-Fiction",
            "published_year": 2020,
        },
        headers=headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "New Title"
    assert data["author"] == "Updated Author"


@pytest.mark.asyncio
async def test_update_book_not_found(client, auth_token):
    """
    Attempt to update a non-existent book.
    Expect: 404 Not Found.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = await client.put(
        "/api/books/99999",
        json={
            "title": "Does Not Exist",
            "author": "Nobody",
            "genre": "Fiction",
            "published_year": 2021,
        },
        headers=headers,
    )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_book(client, auth_token):
    """
    Create a book, delete it, and confirm it no longer exists.
    Expect: 200 OK on delete, 404 on subsequent get.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = await client.post(
        "/api/books",
        json={
            "title": "Delete Me",
            "author": "Tmp",
            "genre": "Science",
            "published_year": 2015,
        },
        headers=headers,
    )
    book_id = resp.json()["id"]

    resp = await client.delete(f"/api/books/{book_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"

    resp = await client.get(f"/api/books/{book_id}")
    assert resp.status_code == 404
