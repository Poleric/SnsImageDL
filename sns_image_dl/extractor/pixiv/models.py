from datetime import datetime
from typing import Literal

from msgspec import Struct

__all__ = (
    "ImageUrls",
    "User",
    "Tag",
    "Series",
    "MetaSinglePage",
    "MetaPage",
    "IllustDetails"
)


class ImageUrls(Struct):
    large: str | None = None
    medium: str | None = None
    square_medium: str | None = None
    original: str | None = None


class User(Struct):
    id: int
    name: str  # display name
    account: str  # account handle
    profile_image_urls: ImageUrls
    is_followed: bool | None = None
    is_access_blocking_user: bool | None = None


class Tag(Struct):
    name: str
    translated_name: str | None = None


class Series(Struct):
    id: int
    title: str


class MetaSinglePage(Struct):
    original_image_url: str | None = None


class MetaPage(Struct):
    image_urls: ImageUrls


class IllustDetails(Struct, kw_only=True):
    id: int
    title: str | Literal["無題", "no title"]  # prob more no title literals for other language, kr, zh
    type: Literal["illust", "ugoira"]
    image_urls: ImageUrls
    caption: str  # description
    restrict: int
    user: User
    tags: list[Tag]
    tools: list[str]
    create_date: datetime  # YYYY-MM-DDTHH:mm:ss+TZ:00
    page_count: int
    width: int
    height: int
    sanity_level: int
    x_restrict: bool  # sfw - 0  nsfw - 1
    series: Series | None = None
    meta_single_page: MetaSinglePage
    meta_pages: list[MetaPage] = []
    total_view: int
    total_bookmarks: int
    is_bookmarked: bool
    visible: bool
    is_muted: bool
    illust_ai_type: int
    illust_book_style: int
    total_comments: int | None = None
    restriction_attributes: list[str] = []
