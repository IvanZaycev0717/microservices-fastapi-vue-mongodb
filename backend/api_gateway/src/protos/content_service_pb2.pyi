from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AboutRequest(_message.Message):
    __slots__ = ("lang",)
    LANG_FIELD_NUMBER: _ClassVar[int]
    lang: str
    def __init__(self, lang: _Optional[str] = ...) -> None: ...

class AboutResponse(_message.Message):
    __slots__ = ("about",)
    ABOUT_FIELD_NUMBER: _ClassVar[int]
    about: _containers.RepeatedCompositeFieldContainer[AboutItem]
    def __init__(self, about: _Optional[_Iterable[_Union[AboutItem, _Mapping]]] = ...) -> None: ...

class AboutItem(_message.Message):
    __slots__ = ("id", "image_url", "title", "description")
    ID_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    image_url: str
    title: str
    description: str
    def __init__(self, id: _Optional[str] = ..., image_url: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class TechRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TechResponse(_message.Message):
    __slots__ = ("kingdoms",)
    KINGDOMS_FIELD_NUMBER: _ClassVar[int]
    kingdoms: _containers.RepeatedCompositeFieldContainer[TechKingdom]
    def __init__(self, kingdoms: _Optional[_Iterable[_Union[TechKingdom, _Mapping]]] = ...) -> None: ...

class TechKingdom(_message.Message):
    __slots__ = ("kingdom", "items")
    KINGDOM_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    kingdom: str
    items: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, kingdom: _Optional[str] = ..., items: _Optional[_Iterable[str]] = ...) -> None: ...

class ProjectsRequest(_message.Message):
    __slots__ = ("lang", "sort")
    LANG_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    lang: str
    sort: str
    def __init__(self, lang: _Optional[str] = ..., sort: _Optional[str] = ...) -> None: ...

class ProjectsResponse(_message.Message):
    __slots__ = ("projects",)
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[ProjectItem]
    def __init__(self, projects: _Optional[_Iterable[_Union[ProjectItem, _Mapping]]] = ...) -> None: ...

class ProjectItem(_message.Message):
    __slots__ = ("id", "title", "thumbnail", "image", "description", "link", "date", "popularity")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    THUMBNAIL_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    POPULARITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    thumbnail: str
    image: str
    description: str
    link: str
    date: str
    popularity: int
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., thumbnail: _Optional[str] = ..., image: _Optional[str] = ..., description: _Optional[str] = ..., link: _Optional[str] = ..., date: _Optional[str] = ..., popularity: _Optional[int] = ...) -> None: ...

class CertificatesRequest(_message.Message):
    __slots__ = ("sort",)
    SORT_FIELD_NUMBER: _ClassVar[int]
    sort: str
    def __init__(self, sort: _Optional[str] = ...) -> None: ...

class CertificatesResponse(_message.Message):
    __slots__ = ("certificates",)
    CERTIFICATES_FIELD_NUMBER: _ClassVar[int]
    certificates: _containers.RepeatedCompositeFieldContainer[CertificateItem]
    def __init__(self, certificates: _Optional[_Iterable[_Union[CertificateItem, _Mapping]]] = ...) -> None: ...

class CertificateItem(_message.Message):
    __slots__ = ("id", "thumb", "src", "date", "popularity", "alt")
    ID_FIELD_NUMBER: _ClassVar[int]
    THUMB_FIELD_NUMBER: _ClassVar[int]
    SRC_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    POPULARITY_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    id: str
    thumb: str
    src: str
    date: str
    popularity: int
    alt: str
    def __init__(self, id: _Optional[str] = ..., thumb: _Optional[str] = ..., src: _Optional[str] = ..., date: _Optional[str] = ..., popularity: _Optional[int] = ..., alt: _Optional[str] = ...) -> None: ...

class PublicationsRequest(_message.Message):
    __slots__ = ("lang", "sort")
    LANG_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    lang: str
    sort: str
    def __init__(self, lang: _Optional[str] = ..., sort: _Optional[str] = ...) -> None: ...

class PublicationsResponse(_message.Message):
    __slots__ = ("publications",)
    PUBLICATIONS_FIELD_NUMBER: _ClassVar[int]
    publications: _containers.RepeatedCompositeFieldContainer[PublicationItem]
    def __init__(self, publications: _Optional[_Iterable[_Union[PublicationItem, _Mapping]]] = ...) -> None: ...

class PublicationItem(_message.Message):
    __slots__ = ("id", "title", "page", "site", "rating", "date")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    SITE_FIELD_NUMBER: _ClassVar[int]
    RATING_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    page: str
    site: str
    rating: int
    date: str
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., page: _Optional[str] = ..., site: _Optional[str] = ..., rating: _Optional[int] = ..., date: _Optional[str] = ...) -> None: ...
