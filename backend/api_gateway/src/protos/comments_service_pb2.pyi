from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateCommentRequest(_message.Message):
    __slots__ = ("project_id", "author_id", "author_email", "comment_text", "parent_comment_id")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_EMAIL_FIELD_NUMBER: _ClassVar[int]
    COMMENT_TEXT_FIELD_NUMBER: _ClassVar[int]
    PARENT_COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    author_id: str
    author_email: str
    comment_text: str
    parent_comment_id: int
    def __init__(self, project_id: _Optional[str] = ..., author_id: _Optional[str] = ..., author_email: _Optional[str] = ..., comment_text: _Optional[str] = ..., parent_comment_id: _Optional[int] = ...) -> None: ...

class CreateCommentResponse(_message.Message):
    __slots__ = ("comment_id", "message")
    COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    comment_id: int
    message: str
    def __init__(self, comment_id: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class GetAllCommentsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllCommentsResponse(_message.Message):
    __slots__ = ("comments",)
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    comments: _containers.RepeatedCompositeFieldContainer[Comment]
    def __init__(self, comments: _Optional[_Iterable[_Union[Comment, _Mapping]]] = ...) -> None: ...

class GetCommentRequest(_message.Message):
    __slots__ = ("comment_id",)
    COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    comment_id: int
    def __init__(self, comment_id: _Optional[int] = ...) -> None: ...

class GetCommentResponse(_message.Message):
    __slots__ = ("comment",)
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    comment: Comment
    def __init__(self, comment: _Optional[_Union[Comment, _Mapping]] = ...) -> None: ...

class GetCommentsByProjectIdRequest(_message.Message):
    __slots__ = ("project_id",)
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    def __init__(self, project_id: _Optional[str] = ...) -> None: ...

class GetCommentsByProjectIdResponse(_message.Message):
    __slots__ = ("comments",)
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    comments: _containers.RepeatedCompositeFieldContainer[Comment]
    def __init__(self, comments: _Optional[_Iterable[_Union[Comment, _Mapping]]] = ...) -> None: ...

class GetCommentsByAuthorIdRequest(_message.Message):
    __slots__ = ("author_id",)
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    author_id: str
    def __init__(self, author_id: _Optional[str] = ...) -> None: ...

class GetCommentsByAuthorIdResponse(_message.Message):
    __slots__ = ("comments",)
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    comments: _containers.RepeatedCompositeFieldContainer[Comment]
    def __init__(self, comments: _Optional[_Iterable[_Union[Comment, _Mapping]]] = ...) -> None: ...

class UpdateCommentRequest(_message.Message):
    __slots__ = ("comment_id", "new_text")
    COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_TEXT_FIELD_NUMBER: _ClassVar[int]
    comment_id: int
    new_text: str
    def __init__(self, comment_id: _Optional[int] = ..., new_text: _Optional[str] = ...) -> None: ...

class UpdateCommentResponse(_message.Message):
    __slots__ = ("comment_id", "message")
    COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    comment_id: int
    message: str
    def __init__(self, comment_id: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class DeleteCommentRequest(_message.Message):
    __slots__ = ("comment_id",)
    COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    comment_id: int
    def __init__(self, comment_id: _Optional[int] = ...) -> None: ...

class DeleteCommentResponse(_message.Message):
    __slots__ = ("comment_id", "message")
    COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    comment_id: int
    message: str
    def __init__(self, comment_id: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class Comment(_message.Message):
    __slots__ = ("id", "project_id", "author_id", "author_email", "comment_text", "created_at", "parent_comment_id", "likes", "dislikes")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_EMAIL_FIELD_NUMBER: _ClassVar[int]
    COMMENT_TEXT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    PARENT_COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    LIKES_FIELD_NUMBER: _ClassVar[int]
    DISLIKES_FIELD_NUMBER: _ClassVar[int]
    id: int
    project_id: str
    author_id: str
    author_email: str
    comment_text: str
    created_at: str
    parent_comment_id: int
    likes: int
    dislikes: int
    def __init__(self, id: _Optional[int] = ..., project_id: _Optional[str] = ..., author_id: _Optional[str] = ..., author_email: _Optional[str] = ..., comment_text: _Optional[str] = ..., created_at: _Optional[str] = ..., parent_comment_id: _Optional[int] = ..., likes: _Optional[int] = ..., dislikes: _Optional[int] = ...) -> None: ...
