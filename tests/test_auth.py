import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "password123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "user@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_conflict(client):
    await client.post(
        "/api/auth/register", json={"email": "dupe@example.com", "password": "pass123"}
    )
    resp = await client.post(
        "/api/auth/register", json={"email": "dupe@example.com", "password": "pass123"}
    )
    assert resp.status_code == 409
    data = resp.json()
    assert data["error"]["code"] == 409
    assert "User with this email already exists" in data["error"]["message"]


@pytest.mark.asyncio
async def test_register_invalid(client):
    resp = await client.post(
        "/api/auth/register", json={"email": "not-an-email", "password": "123"}
    )
    assert resp.status_code == 422
    data = resp.json()

    assert "error" in data
    assert data["error"]["code"] == 422
    assert isinstance(data["error"]["message"], list)
    assert any(err["loc"][-1] == "email" for err in data["error"]["message"])
    assert any(err["loc"][-1] == "password" for err in data["error"]["message"])


@pytest.mark.asyncio
async def test_login_and_me(client):
    await client.post(
        "/api/auth/register", json={"email": "me@example.com", "password": "secret123"}
    )

    resp = await client.post(
        "/api/auth/login", json={"email": "me@example.com", "password": "secret123"}
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

    resp = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_login_invalid(client):
    await client.post(
        "/api/auth/register",
        json={"email": "wronglogin@example.com", "password": "validpass"},
    )

    resp = await client.post(
        "/api/auth/login",
        json={"email": "wronglogin@example.com", "password": "wrongpass"},
    )
    assert resp.status_code == 401
    data = resp.json()
    assert data["error"]["code"] == 401
    assert "Invalid credentials" in data["error"]["message"]
