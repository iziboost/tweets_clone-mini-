from __future__ import annotations
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Media(Base):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_path: Mapped[str] = mapped_column(String(255))

    tweet_id: Mapped[int | None] = mapped_column(
        ForeignKey("tweets.id", ondelete="CASCADE"),
        nullable=True,
    )

    tweet: Mapped["Tweet"] = relationship(back_populates="medias")
