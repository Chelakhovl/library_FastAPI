import pytest


@pytest.mark.asyncio
async def test_recommendations_by_genre(client, auth_token):
    """
    Create books of different genres and request recommendations by genre.
    Expect: 200 OK and only books with matching genre are returned.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}

    await client.post(
        "/api/books",
        json={
            "title": "Fiction Book 1",
            "author": "Author A",
            "genre": "Fiction",
            "published_year": 2001,
        },
        headers=headers,
    )

    await client.post(
        "/api/books",
        json={
            "title": "Science Book 1",
            "author": "Author B",
            "genre": "Science",
            "published_year": 2005,
        },
        headers=headers,
    )

    resp = await client.get("/api/books/recommendations?by=genre&value=Fiction&limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert all(book["genre"] == "Fiction" for book in data)


@pytest.mark.asyncio
async def test_recommendations_by_author(client, auth_token):
    """
    Create books with the same author and request recommendations by author.
    Expect: 200 OK and only books from that author are returned.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}

    await client.post(
        "/api/books",
        json={
            "title": "AuthorTest Book 1",
            "author": "Same Author",
            "genre": "History",
            "published_year": 2010,
        },
        headers=headers,
    )

    await client.post(
        "/api/books",
        json={
            "title": "AuthorTest Book 2",
            "author": "Same Author",
            "genre": "Fiction",
            "published_year": 2012,
        },
        headers=headers,
    )

    resp = await client.get(
        "/api/books/recommendations?by=author&value=Same Author&limit=5"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert all(book["author"] == "Same Author" for book in data)


@pytest.mark.asyncio
async def test_recommendations_not_found(client):
    resp = await client.get("/api/books/recommendations?by=genre&value=Unknown&limit=5")
    assert resp.status_code == 404
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == 404
    assert data["error"]["message"] == "No recommendations found"
