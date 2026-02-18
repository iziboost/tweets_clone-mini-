from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User


async def get_current_user(
    api_key: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Получаем пользователя по API-ключу.
    """

    result = await db.execute(
        select(User).where(User.api_key == api_key)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return user
