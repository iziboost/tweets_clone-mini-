from app.models.follow import Follow
from app.models.user import User
from app.schemas.response import SimpleResult
from app.schemas.error import ErrorResponse

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.api.deps import get_current_user

router = APIRouter(tags=["follows"])


@router.post(
    "/users/{user_id}/follow",
    response_model=SimpleResult,
    responses={200: {"description": "Followed"}, 401: {"model": ErrorResponse}},
)
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SimpleResult:
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    res = await db.execute(select(User).where(User.id == user_id))
    target = res.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")

    follow = Follow(follower_id=current_user.id, following_id=user_id)
    db.add(follow)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()  # уже подписан

    return SimpleResult(result=True)


@router.delete(
    "/users/{user_id}/follow",
    response_model=SimpleResult,
    responses={200: {"description": "Unfollowed"}, 401: {"model": ErrorResponse}},
)
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SimpleResult:
    res = await db.execute(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_id,
        )
    )
    follow = res.scalar_one_or_none()
    if follow:
        await db.delete(follow)
        await db.commit()

    return SimpleResult(result=True)
