from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.like import Like
from app.models.tweet import Tweet
from app.models.user import User
from app.schemas.error import ErrorResponse

router = APIRouter(tags=["likes"])


@router.post(
    "/tweets/{tweet_id}/likes",
    responses={200: {"description": "Liked"}, 401: {"model": ErrorResponse}},
)
async def like_tweet(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    # убеждаемся, что твит существует
    res = await db.execute(select(Tweet).where(Tweet.id == tweet_id))
    tweet = res.scalar_one_or_none()
    if tweet is None:
        raise HTTPException(status_code=404, detail="Tweet not found")

    like = Like(user_id=current_user.id, tweet_id=tweet_id)
    db.add(like)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()  # лайк уже существует — просто считаем операцию успешной

    return {"result": True}


@router.delete(
    "/tweets/{tweet_id}/likes",
    responses={200: {"description": "Unliked"}, 401: {"model": ErrorResponse}},
)
async def unlike_tweet(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    res = await db.execute(
        select(Like).where(
            Like.tweet_id == tweet_id,
            Like.user_id == current_user.id,
        )
    )
    like = res.scalar_one_or_none()
    if like:
        await db.delete(like)
        await db.commit()
    # если лайка нет — просто возвращаем успех (идемпотентность)
    return {"result": True}