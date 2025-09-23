from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(24), nullable=False, index=True
    )
    author_id: Mapped[str] = mapped_column(String(24), nullable=False)
    author_email: Mapped[str] = mapped_column(String(255), nullable=False)
    comment_text: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    parent_comment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("comments.id")
    )
    likes: Mapped[int]
    dislikes: Mapped[int]

    children = relationship("Comment")
