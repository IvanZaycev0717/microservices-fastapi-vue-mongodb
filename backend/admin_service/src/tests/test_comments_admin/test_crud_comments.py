from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.comments_admin.models import Comment


class TestCommentsCRUD:
    async def test_create_comment_database_error(
        self, comments_crud, mock_db_session
    ):
        mock_db_session.flush.side_effect = SQLAlchemyError("DB error")

        comment_data = {
            "project_id": "project123",
            "author_id": "user123",
            "author_email": "user@example.com",
            "comment_text": "Test comment",
            "created_at": None,
            "parent_comment_id": None,
            "likes": 0,
            "dislikes": 0,
        }

        with pytest.raises(ValueError, match="Database error"):
            await comments_crud.create_comment(comment_data)
        mock_db_session.rollback.assert_called_once()

    async def test_read_all_comments_success(
        self, comments_crud, mock_db_session
    ):
        mock_comments = [Mock(spec=Comment), Mock(spec=Comment)]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_comments
        mock_db_session.execute.return_value = mock_result

        comments = await comments_crud.read_all_comments()
        assert len(comments) == 2
        mock_db_session.execute.assert_called_once()

    async def test_read_all_comments_empty(
        self, comments_crud, mock_db_session
    ):
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        comments = await comments_crud.read_all_comments()
        assert len(comments) == 0

    async def test_read_one_comment_found(
        self, comments_crud, mock_db_session
    ):
        mock_comment = Mock(spec=Comment)
        mock_comment.id = 1
        mock_comment.comment_text = "Test comment"

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_comment
        mock_db_session.execute.return_value = mock_result

        comment = await comments_crud.read_one_comment(1)
        assert comment.id == 1
        assert comment.comment_text == "Test comment"

    async def test_read_one_comment_not_found(
        self, comments_crud, mock_db_session
    ):
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(ValueError, match="not found"):
            await comments_crud.read_one_comment(999)

    async def test_update_comment_success(
        self, comments_crud, mock_db_session
    ):
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_db_session.execute.return_value = mock_result

        updated_id = await comments_crud.update_comment(1, "New text")
        assert updated_id == 1
        mock_db_session.commit.assert_called_once()

    async def test_update_comment_not_found(
        self, comments_crud, mock_db_session
    ):
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(ValueError, match="not found"):
            await comments_crud.update_comment(999, "New text")

    async def test_delete_comment_success(
        self, comments_crud, mock_db_session
    ):
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_db_session.execute.return_value = mock_result

        deleted_id = await comments_crud.delete_comment(1)
        assert deleted_id == 1
        mock_db_session.commit.assert_called_once()

    async def test_delete_comment_not_found(
        self, comments_crud, mock_db_session
    ):
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(ValueError, match="not found"):
            await comments_crud.delete_comment(999)

    async def test_set_default_comments_of_banned_user(
        self, comments_crud, mock_db_session
    ):
        mock_result = Mock()
        mock_result.rowcount = 3
        mock_db_session.execute.return_value = mock_result

        updated_count = (
            await comments_crud.set_default_comments_of_banned_user("user123")
        )
        assert updated_count == 3
        mock_db_session.commit.assert_called_once()

    async def test_set_default_comments_no_comments(
        self, comments_crud, mock_db_session
    ):
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_db_session.execute.return_value = mock_result

        updated_count = (
            await comments_crud.set_default_comments_of_banned_user(
                "nonexistent"
            )
        )
        assert updated_count == 0
