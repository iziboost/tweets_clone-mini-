"""Тесты эндпоинтов follow/unfollow."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_follow_user(client_test: AsyncClient, client_admin: AsyncClient) -> None:
    """Test подписывается на Admin."""
    me_resp = await client_admin.get("/api/users/me")
    admin_id = me_resp.json()["user"]["id"]

    response = await client_test.post(f"/api/users/{admin_id}/follow")
    assert response.status_code == 200
    assert response.json() == {"result": True}

    # В профиле Test теперь Admin в following
    me_resp = await client_test.get("/api/users/me")
    following = me_resp.json()["user"]["following"]
    assert any(u["id"] == admin_id and u["name"] == "Admin" for u in following)


@pytest.mark.asyncio
async def test_follow_self_forbidden(client_test: AsyncClient) -> None:
    """Нельзя подписаться на себя."""
    me_resp = await client_test.get("/api/users/me")
    my_id = me_resp.json()["user"]["id"]

    response = await client_test.post(f"/api/users/{my_id}/follow")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_follow_nonexistent(client_test: AsyncClient) -> None:
    """Подписка на несуществующего пользователя — 404."""
    response = await client_test.post("/api/users/99999/follow")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unfollow_user(
    client_test: AsyncClient, client_admin: AsyncClient
) -> None:
    """Test отписывается от Admin."""
    me_resp = await client_admin.get("/api/users/me")
    admin_id = me_resp.json()["user"]["id"]

    # Сначала подписываемся
    await client_test.post(f"/api/users/{admin_id}/follow")

    # Отписываемся
    response = await client_test.delete(f"/api/users/{admin_id}/follow")
    assert response.status_code == 200
    assert response.json() == {"result": True}

    # В following Admin больше нет
    me_resp = await client_test.get("/api/users/me")
    following = me_resp.json()["user"]["following"]
    assert not any(u["id"] == admin_id for u in following)


@pytest.mark.asyncio
async def test_unfollow_idempotent(client_test: AsyncClient, client_admin: AsyncClient) -> None:
    """Повторный unfollow — успех (идемпотентность)."""
    me_resp = await client_admin.get("/api/users/me")
    admin_id = me_resp.json()["user"]["id"]

    # Дважды отписываемся (ни разу не подписывались)
    r1 = await client_test.delete(f"/api/users/{admin_id}/follow")
    r2 = await client_test.delete(f"/api/users/{admin_id}/follow")
    assert r1.status_code == 200
    assert r2.status_code == 200
