from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from comments_admin.models import Comment

async def create_comment(db_session: AsyncSession, comment_data: dict):
    comment = Comment(**comment_data)
    async with db_session.begin():
        db_session.add(comment)
        await db_session.flush()
        comment_id = comment.id
        await db_session.commit()
    return comment_id