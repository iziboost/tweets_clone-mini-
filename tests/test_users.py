"""Тесты эндпоинтов пользователей: /me и /users/{id}."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_me(client_test: AsyncClient) -> None:
    """GET /api/users/me возвращает профиль текущего пользователя."""
    response = await client_test.get("/api/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    user = data["user"]
    assert user["name"] == "Test"
    assert "id" in user
    assert "followers" in user
    assert "following" in user
    assert isinstance(user["followers"], list)
    assert isinstance(user["following"], list)


@pytest.mark.asyncio
async def test_get_me_admin(client_admin: AsyncClient) -> None:
    """GET /api/users/me для admin возвращает Admin."""
    response = await client_admin.get("/api/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["name"] == "Admin"


@pytest.mark.asyncio
async def test_get_user_by_id(
    client_test: AsyncClient, client_admin: AsyncClient
) -> None:
    """GET /api/users/{id} возвращает профиль по id (без auth)."""
    # Получаем id admin через /me
    me_resp = await client_admin.get("/api/users/me")
    admin_id = me_resp.json()["user"]["id"]

    # Запрашиваем профиль admin (можно без api-key — эндпоинт публичный)
    response = await client_test.get(f"/api/users/{admin_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert data["user"]["name"] == "Admin"
    assert data["user"]["id"] == admin_id


@pytest.mark.asyncio
async def test_get_user_not_found(client_test: AsyncClient) -> None:
    """GET /api/users/99999 — 404."""
    response = await client_test.get("/api/users/99999")
    assert response.status_code == 404
