from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.follow import Follow
from app.models.like import Like
from app.models.media import Media
from app.models.tweet import Tweet
from app.models.user import User
from app.schemas.error import ErrorResponse
from app.schemas.tweet import CreateTweet

router = APIRouter(tags=["tweets"])


@router.post(
    "/tweets",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Tweet created"},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
    },
)
async def create_tweet(
    payload: CreateTweet,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    tweet = Tweet(content=payload.tweet_data, author_id=current_user.id)
    db.add(tweet)
    await db.flush()  # получаем tweet.id без отдельного запроса

    if payload.tweet_media_ids:
        stmt = (
            update(Media)
            .where(Media.id.in_(payload.tweet_media_ids))
            .values(tweet_id=tweet.id)
        )
        await db.execute(stmt)

    await db.commit()
    return {"result": True, "tweet_id": tweet.id}


@router.delete(
    "/tweets/{tweet_id}",
    responses={
        200: {"description": "Tweet deleted"},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def delete_tweet(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(select(Tweet).where(Tweet.id == tweet_id))
    tweet = result.scalar_one_or_none()

    if tweet is None:
        raise HTTPException(status_code=404, detail="Tweet not found")

    if tweet.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot delete foreign tweet")

    await db.delete(tweet)
    await db.commit()
    return {"result": True}


@router.get(
    "/tweets",
    responses={401: {"model": ErrorResponse}},
)
async def get_feed(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    # сначала id тех, кого я фоловлю
    subq = select(Follow.following_id).where(Follow.follower_id == current_user.id)

    stmt = (
        select(Tweet)
        .where(
            or_(
                Tweet.author_id.in_(subq),
                Tweet.author_id == current_user.id,  # также показываем свои твиты
            )
        )
        .options(
            selectinload(Tweet.author),
            selectinload(Tweet.medias),
            selectinload(Tweet.likes).selectinload(Like.user),
        )
        .outerjoin(Like)
        .group_by(Tweet.id)
        .order_by(desc(func.count(Like.id)), desc(Tweet.created_at))
    )

    result = await db.execute(stmt)
    tweets: list[Tweet] = list(result.scalars().unique().all())

    items = []
    for t in tweets:
        attachments = [m.file_path for m in t.medias]  # можно превратить в URL
        likes = [
            {"user_id": lk.user.id, "name": lk.user.name}
            for lk in t.likes
        ]
        items.append({
            "id": t.id,
            "content": t.content,
            "attachments": attachments,
            "author": {
                "id": t.author.id,
                "name": t.author.name,
            },
            "likes": likes,
        })

    return {"result": True, "tweets": items}