"""Тесты ленты: твиты от тех, на кого подписан."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_feed_shows_following_tweets(
    client_test: AsyncClient, client_admin: AsyncClient
) -> None:
    """Лента Test показывает твиты Admin после подписки."""
    # Получаем id admin
    me_resp = await client_admin.get("/api/users/me")
    admin_id = me_resp.json()["user"]["id"]

    # Admin создаёт твит
    create_resp = await client_admin.post(
        "/api/tweets",
        json={"tweet_data": "Твит от Admin"},
    )
    assert create_resp.status_code == 201

    # Test пока не подписан — в ленте Test нет твита Admin
    feed_before = await client_test.get("/api/tweets")
    assert len(feed_before.json()["tweets"]) == 0

    # Test подписывается
    await client_test.post(f"/api/users/{admin_id}/follow")

    # Теперь в ленте Test есть твит Admin
    feed_after = await client_test.get("/api/tweets")
    tweets = feed_after.json()["tweets"]
    assert len(tweets) == 1
    assert tweets[0]["content"] == "Твит от Admin"
    assert tweets[0]["author"]["name"] == "Admin"
