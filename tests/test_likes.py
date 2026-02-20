"""Тесты эндпоинтов like/unlike."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_like_tweet(client_test: AsyncClient) -> None:
    """Поставить лайк на твит."""
    # Создаём твит
    create_resp = await client_test.post(
        "/api/tweets",
        json={"tweet_data": "Tweet to like"},
    )
    tweet_id = create_resp.json()["tweet_id"]

    # Ставим лайк
    like_resp = await client_test.post(f"/api/tweets/{tweet_id}/likes")
    assert like_resp.status_code == 200
    assert like_resp.json() == {"result": True}

    # В ленте твит имеет 1 лайк
    feed_resp = await client_test.get("/api/tweets")
    tweets = feed_resp.json()["tweets"]
    assert len(tweets) == 1
    assert len(tweets[0]["likes"]) == 1
    assert tweets[0]["likes"][0]["name"] == "Test"


@pytest.mark.asyncio
async def test_unlike_tweet(client_test: AsyncClient) -> None:
    """Убрать лайк с твита."""
    create_resp = await client_test.post(
        "/api/tweets",
        json={"tweet_data": "Tweet"},
    )
    tweet_id = create_resp.json()["tweet_id"]
    await client_test.post(f"/api/tweets/{tweet_id}/likes")

    # Убираем лайк
    unlike_resp = await client_test.delete(f"/api/tweets/{tweet_id}/likes")
    assert unlike_resp.status_code == 200
    assert unlike_resp.json() == {"result": True}

    # В ленте 0 лайков
    feed_resp = await client_test.get("/api/tweets")
    assert feed_resp.json()["tweets"][0]["likes"] == []


@pytest.mark.asyncio
async def test_like_twice_idempotent(client_test: AsyncClient) -> None:
    """Повторный лайк — успех (идемпотентность)."""
    create_resp = await client_test.post(
        "/api/tweets",
        json={"tweet_data": "Tweet"},
    )
    tweet_id = create_resp.json()["tweet_id"]

    r1 = await client_test.post(f"/api/tweets/{tweet_id}/likes")
    r2 = await client_test.post(f"/api/tweets/{tweet_id}/likes")
    assert r1.status_code == 200
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_unlike_idempotent(client_test: AsyncClient) -> None:
    """unlike без предшествующего like — успех."""
    create_resp = await client_test.post(
        "/api/tweets",
        json={"tweet_data": "Tweet"},
    )
    tweet_id = create_resp.json()["tweet_id"]

    response = await client_test.delete(f"/api/tweets/{tweet_id}/likes")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_like_nonexistent_tweet(client_test: AsyncClient) -> None:
    """Лайк несуществующего твита — 404."""
    response = await client_test.post("/api/tweets/99999/likes")
    assert response.status_code == 404
