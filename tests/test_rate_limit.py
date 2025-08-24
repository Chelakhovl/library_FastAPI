import pytest


@pytest.mark.asyncio
async def test_rate_limit_exceeded(client, auth_token):
    """
    Exceed the allowed rate limit by sending multiple requests quickly.
    Expect: at least one request returns 429 Too Many Requests
    with custom error format.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}

    responses = [await client.get("api/books", headers=headers) for _ in range(100)]

    assert any(r.status_code == 429 for r in responses)

    too_many = next(r for r in responses if r.status_code == 429)
    data = too_many.json()
    assert "error" in data
    assert data["error"]["code"] == 429
    assert "Too many requests" in data["error"]["message"]


@pytest.mark.asyncio
async def test_rate_limit_unauthorized(client):
    """
    Request the /books endpoint without a token.
    Expect: 429 Too Many Requests (rate limit still applies).
    """
    responses = [await client.get("api/books") for _ in range(100)]

    assert any(r.status_code == 429 for r in responses)

    too_many = next(r for r in responses if r.status_code == 429)
    data = too_many.json()
    assert "error" in data
    assert data["error"]["code"] == 429
    assert "too many requests" in data["error"]["message"].lower()
