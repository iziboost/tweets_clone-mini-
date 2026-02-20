import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Задаём до импорта app, чтобы database.py использовал тестовую БД.
# Файловый SQLite, а не :memory:, чтобы несколько соединений
# (client_test и client_admin в одном тесте) видели одни и те же данные.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import Base, async_session_factory, engine
from app.main import app
from app.models.follow import Follow  # noqa: F401 — регистрируют модели в Base.metadata
from app.models.like import Like  # noqa: F401
from app.models.media import Media  # noqa: F401
from app.models.tweet import Tweet  # noqa: F401
from app.models.user import User

API_KEY_TEST = "test"
API_KEY_ADMIN = "admin"


@pytest_asyncio.fixture
async def db():
    """
    Создаёт таблицы и тестовых пользователей перед тестом,
    удаляет все таблицы после теста.
    Все клиентские фикстуры зависят от этой, чтобы гарантировать
    одну БД на тест и полную изоляцию между тестами.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        for name, key in [("Test", API_KEY_TEST), ("Admin", API_KEY_ADMIN)]:
            res = await session.execute(select(User).where(User.api_key == key))
            if res.scalar_one_or_none() is None:
                session.add(User(name=name, api_key=key))
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db: None) -> AsyncClient:
    """Неаутентифицированный клиент."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def client_test(db: None) -> AsyncClient:
    """Клиент, аутентифицированный как пользователь Test."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"api-key": API_KEY_TEST},
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def client_admin(db: None) -> AsyncClient:
    """Клиент, аутентифицированный как пользователь Admin."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"api-key": API_KEY_ADMIN},
    ) as ac:
        yield ac
