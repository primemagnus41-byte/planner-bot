from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class IdeaTag(Base):
    __tablename__ = "idea_tags"
    idea_id: Mapped[int] = mapped_column(ForeignKey("ideas.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(64))
    __table_args__ = (UniqueConstraint("user_id", "name"),)


class Idea(Base, TimestampMixin):
    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(32), index=True, default=None)
    is_starred: Mapped[bool] = mapped_column(default=False, index=True)
    source: Mapped[str] = mapped_column(String(16), default="text")  # text | voice | forward
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)

    tags: Mapped[list[Tag]] = relationship(secondary="idea_tags")
