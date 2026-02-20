from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.follow import Follow
from app.models.user import User
from app.schemas.error import ErrorResponse

router = APIRouter(tags=["users"])


def build_profile(u: User) -> dict:
    followers = [{"id": f.follower.id, "name": f.follower.name} for f in u.followers]
    following = [{"id": f.following.id, "name": f.following.name} for f in u.followings]
    return {
        "id": u.id,
        "name": u.name,
        "followers": followers,
        "following": following,
    }


@router.get(
    "/users/me",
    responses={200: {"description": "Current user"}, 401: {"model": ErrorResponse}},
)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    stmt = (
        select(User)
        .where(User.id == current_user.id)
        .options(
            selectinload(User.followers).selectinload(Follow.follower),
            selectinload(User.followings).selectinload(Follow.following),
        )
    )
    res = await db.execute(stmt)
    user = res.scalar_one()

    profile = build_profile(user)
    return {"result": True, "user": profile}


@router.get(
    "/users/{user_id}",
    responses={200: {"description": "User profile"}, 404: {"model": ErrorResponse}},
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.followers).selectinload(Follow.follower),
            selectinload(User.followings).selectinload(Follow.following),
        )
    )
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    profile = build_profile(user)
    return {"result": True, "user": profile}
