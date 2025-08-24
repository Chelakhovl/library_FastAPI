import pytest
import io


@pytest.mark.asyncio
async def test_import_books_json_success(client, auth_token):
    """
    Import books from a valid JSON file.
    Expect: 200 OK, at least 2 records imported.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    books_json = io.BytesIO(
        b"""
    [
        {"title": "Book JSON 1", "author": "Author JSON", "genre": "Fiction", "published_year": 2001},
        {"title": "Book JSON 2", "author": "Author JSON", "genre": "Science", "published_year": 2005}
    ]
    """
    )
    resp = await client.post(
        "api/books/import",
        headers=headers,
        files={"file": ("books.json", books_json, "application/json")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "imported" in data and data["imported"] >= 2


@pytest.mark.asyncio
async def test_import_books_csv_success(client, auth_token):
    """
    Import books from a valid CSV file.
    Expect: 200 OK, at least 2 records imported.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    books_csv = io.BytesIO(
        b"title,author,genre,published_year\n"
        b"Book CSV 1,Author CSV,Fiction,1999\n"
        b"Book CSV 2,Author CSV,History,2010\n"
    )
    resp = await client.post(
        "api/books/import",
        headers=headers,
        files={"file": ("books.csv", books_csv, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "imported" in data and data["imported"] >= 2


@pytest.mark.asyncio
async def test_import_books_invalid_json(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    bad_json = io.BytesIO(b'{"title": "Bad"}')
    resp = await client.post(
        "api/books/import",
        headers=headers,
        files={"file": ("bad.json", bad_json, "application/json")},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == 400
    assert "import failed" in data["error"]["message"].lower()


@pytest.mark.asyncio
async def test_import_books_invalid_csv(client, auth_token):
    """
    Attempt to import CSV with invalid records (missing fields).
    Expect: 200 OK but with errors in response.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    bad_csv = io.BytesIO(b"title,author\nOnlyTitle,OnlyAuthor\n")
    resp = await client.post(
        "api/books/import",
        headers=headers,
        files={"file": ("bad.csv", bad_csv, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "errors" in data and len(data["errors"]) > 0


@pytest.mark.asyncio
async def test_export_books_json(client, auth_token):
    """
    Export books in JSON format.
    Expect: 200 OK, application/json, list of books.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    await client.post(
        "api/books",
        json={
            "title": "Export JSON",
            "author": "Test Export",
            "genre": "Science",
            "published_year": 2020,
        },
        headers=headers,
    )

    resp = await client.get("/books/export?format=json", headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/json"
    data = resp.json()
    assert isinstance(data, list)
    assert any(b["title"] == "Export JSON" for b in data)


@pytest.mark.asyncio
async def test_export_books_json(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    await client.post(
        "api/books",
        json={
            "title": "Export JSON",
            "author": "Test Export",
            "genre": "Science",
            "published_year": 2020,
        },
        headers=headers,
    )

    resp = await client.get("api/books/export?format=json", headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/json"
    data = resp.json()
    assert isinstance(data, list)
    assert any(b["title"] == "Export JSON" for b in data)


@pytest.mark.asyncio
async def test_export_books_csv(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    await client.post(
        "api/books",
        json={
            "title": "Export CSV",
            "author": "Test Export",
            "genre": "History",
            "published_year": 2015,
        },
        headers=headers,
    )

    resp = await client.get("api/books/export?format=csv", headers=headers)
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    content = resp.text
    assert "Export CSV" in content
    assert "History" in content
