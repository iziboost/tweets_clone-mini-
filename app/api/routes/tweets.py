from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, func, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.follow import Follow
from app.models.tweet import Tweet
from app.models.media import Media
from app.models.like import Like
from app.models.user import User

from app.schemas.tweet import CreateTweet, CreateTweetResponse, FeedTweet, LikeInfo
from app.schemas.response import SimpleResult, BaseResponse
from app.schemas.error import ErrorResponse
from app.schemas.user import UserShort

router = APIRouter(tags=["tweets"])


@router.post(
    "/tweets",
    response_model=CreateTweetResponse,
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
) -> CreateTweetResponse:
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
    return CreateTweetResponse(result=True, tweet_id=tweet.id)


@router.delete(
    "/tweets/{tweet_id}",
    response_model=SimpleResult,
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
) -> SimpleResult:
    result = await db.execute(select(Tweet).where(Tweet.id == tweet_id))
    tweet = result.scalar_one_or_none()

    if tweet is None:
        raise HTTPException(status_code=404, detail="Tweet not found")

    if tweet.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot delete foreign tweet")

    await db.delete(tweet)
    await db.commit()
    return SimpleResult(result=True)


@router.get(
    "/tweets",
    response_model=BaseResponse[list[FeedTweet]],
    responses={401: {"model": ErrorResponse}},
)
async def get_feed(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    # сначала id тех, кого я фоловлю
    subq = select(Follow.following_id).where(Follow.follower_id == current_user.id)

    stmt = (
        select(Tweet)
        .where(Tweet.author_id.in_(subq))
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

    items: list[FeedTweet] = []
    for t in tweets:
        attachments = [m.file_path for m in t.medias]  # можно превратить в URL
        likes = [
            LikeInfo(user_id=l.user.id, name=l.user.name)
            for l in t.likes
        ]
        items.append(
            FeedTweet(
                id=t.id,
                content=t.content,
                attachments=attachments,
                author=UserShort(id=t.author.id, name=t.author.name),
                likes=likes,
            )   
        )

    return BaseResponse[list[FeedTweet]](result=True, data=items)