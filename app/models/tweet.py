from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.like import Like
    from app.models.media import Media
    from app.models.user import User


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String(280))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped[User] = relationship(back_populates="tweets")

    medias: Mapped[list[Media]] = relationship(
        back_populates="tweet",
        cascade="all, delete-orphan",
    )

    likes: Mapped[list[Like]] = relationship(
        back_populates="tweet",
        cascade="all, delete-orphan",
    )
