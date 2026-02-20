from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.follow import Follow
    from app.models.like import Like
    from app.models.tweet import Tweet


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    api_key: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    # one-to-many: user → tweets
    tweets: Mapped[list[Tweet]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )

    # many-to-many через таблицу likes
    liked_tweets: Mapped[list[Like]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # подписчики
    followers: Mapped[list[Follow]] = relationship(
        foreign_keys="Follow.following_id",
        back_populates="following",
        cascade="all, delete-orphan",
    )

    followings: Mapped[list[Follow]] = relationship(
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )
