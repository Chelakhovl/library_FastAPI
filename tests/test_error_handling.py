import pytest


@pytest.mark.asyncio
async def test_get_nonexistent_book(client):
    """
    Attempt to fetch a non-existent book by ID.
    Expect: 404 Not Found with proper error response.
    """
    resp = await client.get("api/books/99999")
    assert resp.status_code == 404
    data = resp.json()
    assert data["error"]["code"] == 404
    assert data["error"]["message"] == "Book not found"


@pytest.mark.asyncio
async def test_register_duplicate_user(client):
    """
    Attempt to register with an email that already exists.
    Expect: 409 Conflict with descriptive error message.
    """
    await client.post(
        "api/auth/register", json={"email": "dup@example.com", "password": "pass123"}
    )
    resp = await client.post(
        "api/auth/register", json={"email": "dup@example.com", "password": "pass123"}
    )

    assert resp.status_code == 409
    data = resp.json()
    assert data["error"]["code"] == 409
    assert "already exists" in data["error"]["message"]
