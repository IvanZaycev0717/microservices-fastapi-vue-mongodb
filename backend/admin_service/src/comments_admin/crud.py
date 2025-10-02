from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from comments_admin.models import Comment


class CommentsCRUD:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    # CREATE
    async def create_comment(self, comment_data: dict) -> int:
        """Create a new comment in the database.

        Args:
            comment_data (dict): Dictionary containing comment attributes.

        Returns:
            int: ID of the newly created comment.

        Raises:
            ValueError: If database operation fails.
        """
        try:
            comment = Comment(**comment_data)
            self.db_session.add(comment)
            await self.db_session.flush()
            comment_id = comment.id
            await self.db_session.commit()
            return comment_id
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise ValueError(f"Database error: {str(e)}")

    # READ
    async def read_all_comments(self) -> list[Comment]:
        """Retrieve all comments from the database.

        Returns:
            list[Comment]: List of all comments ordered by creation date descending.

        Raises:
            ValueError: If database operation fails.
        """
        try:
            stmt = select(Comment).order_by(Comment.created_at.desc())
            result = await self.db_session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise ValueError(f"Database error reading comments: {str(e)}")

    async def read_one_comment(self, comment_id: int) -> Comment:
        """Retrieve a specific comment by ID.

        Args:
            comment_id (int): ID of the comment to retrieve.

        Returns:
            Comment: Comment object with the specified ID.

        Raises:
            ValueError: If comment not found or database operation fails.
        """
        try:
            stmt = select(Comment).where(Comment.id == comment_id)
            result = await self.db_session.execute(stmt)
            comment = result.scalar_one_or_none()
            if not comment:
                raise ValueError(f"Comment with id={comment_id} not found")
            return comment
        except SQLAlchemyError as e:
            raise ValueError(f"Database error reading comment: {str(e)}")

    async def get_comments_by_project_id(
        self, project_id: str
    ) -> list[Comment]:
        """Retrieve all comments for a specific project.

        Args:
            project_id (str): ID of the project to retrieve comments for.

        Returns:
            list[Comment]: List of comments for the project ordered by creation date descending.

        Raises:
            ValueError: If no comments found or database operation fails.
        """
        try:
            stmt = (
                select(Comment)
                .where(Comment.project_id == project_id)
                .order_by(Comment.created_at.desc())
            )
            result = await self.db_session.execute(stmt)
            comments = result.scalars().all()

            if not comments:
                raise ValueError(f"No comments found for project {project_id}")

            return comments
        except SQLAlchemyError as e:
            raise ValueError(
                f"Database error reading comments for project {project_id}: {str(e)}"
            )

    # UPDATE
    async def update_comment(self, comment_id: int, new_text: str) -> int:
        """Update the text of a specific comment.

        Args:
            comment_id (int): ID of the comment to update.
            new_text (str): New text content for the comment.

        Returns:
            int: ID of the updated comment.

        Raises:
            ValueError: If comment not found or database operation fails.
        """
        try:
            stmt = (
                update(Comment)
                .where(Comment.id == comment_id)
                .values(comment_text=new_text)
            )
            result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            if result.rowcount == 0:
                raise ValueError(f"Comment with id={comment_id} not found")
            return comment_id
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise ValueError(f"Database error updating comment: {str(e)}")

    # DELETE
    async def delete_comment(self, comment_id: int) -> int:
        """Delete a specific comment from the database.

        Args:
            comment_id (int): ID of the comment to delete.

        Returns:
            int: ID of the deleted comment.

        Raises:
            ValueError: If comment not found or database operation fails.
        """
        try:
            stmt = delete(Comment).where(Comment.id == comment_id)
            result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            if result.rowcount == 0:
                raise ValueError(f"Comment with id={comment_id} not found")
            return comment_id
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise ValueError(f"Database error deleting comment: {str(e)}")

    # SET DEFAULT COMMENTS OF BANNED USER
    async def set_default_comments_of_banned_user(self, author_id: str) -> int:
        """Update all comments from a banned user to default text.

        Args:
            author_id (str): ID of the banned user.

        Returns:
            int: Number of comments that were updated.

        Raises:
            ValueError: If database operation fails.
        """
        try:
            stmt = (
                update(Comment)
                .where(Comment.author_id == author_id)
                .values(comment_text="Пользователь был забанен")
            )
            result = await self.db_session.execute(stmt)
            await self.db_session.commit()

            updated_count = result.rowcount
            return updated_count
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise ValueError(f"Database error banning user comments: {str(e)}")
