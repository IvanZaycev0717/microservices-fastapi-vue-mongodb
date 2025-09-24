from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from comments_admin.models import Comment
from sqlalchemy.exc import SQLAlchemyError


class CommentsCRUD:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    # CREATE
    async def create_comment(self, comment_data: dict):
        try:
            comment = Comment(**comment_data)
            async with self.db_session.begin():
                self.db_session.add(comment)
                await self.db_session.flush()
                comment_id = comment.id
                await self.db_session.commit()
            return comment_id
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise ValueError(f"Database error: {str(e)}")
    
    # READ
    async def read_all_comments(self):
        try:
            stmt = select(Comment).order_by(Comment.created_at.desc())
            result = await self.db_session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise ValueError(f"Database error reading comments: {str(e)}")
