"""Тесты эндпоинтов твитов: создание, удаление, лента."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_tweet(client_test: AsyncClient) -> None:
    """Создание твита возвращает 201 и tweet_id."""
    response = await client_test.post(
        "/api/tweets",
        json={"tweet_data": "Hello, world!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["result"] is True
    assert "tweet_id" in data
    assert isinstance(data["tweet_id"], int)


@pytest.mark.asyncio
async def test_create_tweet_with_media_ids(client_test: AsyncClient) -> None:
    """Создание твита с tweet_media_ids (пустой список допустим)."""
    response = await client_test.post(
        "/api/tweets",
        json={"tweet_data": "Tweet with media", "tweet_media_ids": []},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["result"] is True
    assert "tweet_id" in data


@pytest.mark.asyncio
async def test_create_tweet_unauthorized(client: AsyncClient) -> None:
    """Без api-key возвращается 422 (отсутствует header)."""
    response = await client.post(
        "/api/tweets",
        json={"tweet_data": "Hello"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_feed_empty(client_test: AsyncClient) -> None:
    """Пустая лента для нового пользователя (без твитов)."""
    response = await client_test.get("/api/tweets")
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert data["tweets"] == []


@pytest.mark.asyncio
async def test_get_feed_shows_own_tweets(client_test: AsyncClient) -> None:
    """Лента показывает свои твиты."""
    # Создаём твит
    create_resp = await client_test.post(
        "/api/tweets",
        json={"tweet_data": "Мой твит"},
    )
    assert create_resp.status_code == 201
    tweet_id = create_resp.json()["tweet_id"]

    # Проверяем ленту
    feed_resp = await client_test.get("/api/tweets")
    assert feed_resp.status_code == 200
    data = feed_resp.json()
    assert data["result"] is True
    assert len(data["tweets"]) == 1
    tweet = data["tweets"][0]
    assert tweet["id"] == tweet_id
    assert tweet["content"] == "Мой твит"
    assert "author" in tweet
    assert tweet["author"]["name"] == "Test"
    assert tweet["attachments"] == []
    assert tweet["likes"] == []


@pytest.mark.asyncio
async def test_delete_own_tweet(client_test: AsyncClient) -> None:
    """Пользователь может удалить свой твит."""
    create_resp = await client_test.post(
        "/api/tweets",
        json={"tweet_data": "To delete"},
    )
    assert create_resp.status_code == 201
    tweet_id = create_resp.json()["tweet_id"]

    delete_resp = await client_test.delete(f"/api/tweets/{tweet_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json() == {"result": True}

    # Твит удалён, в ленте его нет
    feed_resp = await client_test.get("/api/tweets")
    assert feed_resp.json()["tweets"] == []


@pytest.mark.asyncio
async def test_delete_foreign_tweet_forbidden(
    client_test: AsyncClient, client_admin: AsyncClient
) -> None:
    """Нельзя удалить чужой твит."""
    # Admin создаёт твит
    create_resp = await client_admin.post(
        "/api/tweets",
        json={"tweet_data": "Admin tweet"},
    )
    assert create_resp.status_code == 201
    tweet_id = create_resp.json()["tweet_id"]

    # Test пытается удалить — 403
    delete_resp = await client_test.delete(f"/api/tweets/{tweet_id}")
    assert delete_resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_nonexistent_tweet(client_test: AsyncClient) -> None:
    """Удаление несуществующего твита — 404."""
    response = await client_test.delete("/api/tweets/99999")
    assert response.status_code == 404
