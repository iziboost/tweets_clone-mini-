from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Follow(Base):
    __tablename__ = "follows"

    __table_args__ = (UniqueConstraint("follower_id", "following_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    following_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    follower: Mapped[User] = relationship(
        foreign_keys=[follower_id],
        back_populates="followings",
    )

    following: Mapped[User] = relationship(
        foreign_keys=[following_id],
        back_populates="followers",
    )
