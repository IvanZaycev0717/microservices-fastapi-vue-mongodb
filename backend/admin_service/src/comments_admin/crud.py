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
            async with self.db_session as session:
                comments = await session.execute(stmt)
                return comments.scalars().all()
        except SQLAlchemyError as e:
            raise ValueError(f"Database error reading comments: {str(e)}")
    
    async def read_one_comment(self, comment_id: int):
        try:
            stmt = select(Comment).where(Comment.id == comment_id)
            async with self.db_session as session:
                result = await session.execute(stmt)
                comment = result.scalar_one_or_none()
                if not comment:
                    raise ValueError(f"Comment with id={comment_id} not found")
                return comment
        except SQLAlchemyError as e:
            raise ValueError(f"Database error reading comment: {str(e)}")
    
    # UPDATE

