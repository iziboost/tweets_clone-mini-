from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.tweet import Tweet
    from app.models.user import User


class Like(Base):
    __tablename__ = "likes"

    __table_args__ = (UniqueConstraint("user_id", "tweet_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id", ondelete="CASCADE"))

    user: Mapped[User] = relationship(back_populates="liked_tweets")
    tweet: Mapped[Tweet] = relationship(back_populates="likes")
