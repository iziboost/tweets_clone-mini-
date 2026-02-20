from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.router import api_router
from app.core.database import Base, async_session_factory, engine
from app.models.follow import Follow  # noqa: F401
from app.models.like import Like  # noqa: F401
from app.models.media import Media  # noqa: F401
from app.models.tweet import Tweet  # noqa: F401
from app.models.user import User


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # Создаём первого пользователя (test)
        res = await session.execute(select(User).where(User.api_key == "test"))
        user = res.scalar_one_or_none()
        if user is None:
            session.add(User(name="Test", api_key="test"))
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()

        # Создаём второго пользователя (admin)
        res = await session.execute(select(User).where(User.api_key == "admin"))
        admin_user = res.scalar_one_or_none()
        if admin_user is None:
            session.add(User(name="Admin", api_key="admin"))
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()

    yield

    # Shutdown (если нужно что-то закрыть)


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "API is running"}
