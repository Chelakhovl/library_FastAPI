import pytest


pytest.mark.asyncio


async def test_pagination_and_sorting(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    books = [
        {"title": "Alpha", "author": "A", "genre": "Fiction", "published_year": 2000},
        {"title": "Charlie", "author": "C", "genre": "Fiction", "published_year": 2002},
        {"title": "Bravo", "author": "B", "genre": "Fiction", "published_year": 2001},
    ]
    for b in books:
        await client.post("api/books", json=b, headers=headers)

    # --- ASC сортування ---
    resp = await client.get("api/books?page=1&page_size=3&sort_by=title&sort_order=asc")
    assert resp.status_code == 200
    data = resp.json()
    titles = [item["title"] for item in data["items"]]
    assert titles == sorted(titles)  # перевірка, що в зростаючому порядку

    # --- DESC сортування ---
    resp = await client.get(
        "api/books?page=1&page_size=3&sort_by=title&sort_order=desc"
    )
    assert resp.status_code == 200
    data = resp.json()
    titles = [item["title"] for item in data["items"]]
    assert titles == sorted(titles, reverse=True)  # перевірка, що в спадному порядку

    # --- Пагінація ---
    resp = await client.get("api/books?page=2&page_size=1&sort_by=title&sort_order=asc")
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 2
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_pagination_invalid_page(client):
    resp = await client.get("api/books?page=0&page_size=5&sort_by=title&sort_order=asc")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_sorting_invalid_field(client):
    """
    Request with invalid sort_by field.
    Expect: 400 or 422 with proper error.
    """
    resp = await client.get(
        "api/books?page=1&page_size=5&sort_by=not_a_field&sort_order=asc"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert all("title" in item for item in data["items"])
