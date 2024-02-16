from typing import Sequence, TypedDict, Literal

type UrlLike = str


class ImageSource(TypedDict, total=False):
    large: UrlLike
    medium: UrlLike
    square_medium: UrlLike
    original: UrlLike


class IllustDetails(TypedDict):
    class User(TypedDict):
        account: str  # account handle?
        id: int
        is_followed: bool
        name: str  # display name
        profile_image_urls: ImageSource

    class Tag(TypedDict):
        name: str
        translated_name: str | None

    class MetaSinglePage(TypedDict):
        original_image_url: UrlLike

    class MetaPage(TypedDict):
        image_urls: ImageSource

    id: int
    title: str | Literal["無題", "no title"]  # prob more no title literals for other language, kr, zh
    type: Literal["illust", "ugoira"]
    image_urls: ImageSource
    caption: str  # description
    restrict: int
    user: User
    tags: Sequence[Tag]
    tools: Sequence[str]
    create_date: str  # YYYY-MM-DDTHH:mm:ss+TZ:00
    page_count: int
    width: int
    height: int
    sanity_level: int
    x_restrict: int  # sfw - 0  nsfw - 1
    series: str | None  # TODO: double check
    meta_single_page: MetaSinglePage  # check
    meta_pages: Sequence[MetaPage]
    total_view: int
    total_bookmarks: int
    is_bookmarked: bool
    visible: bool
    is_muted: bool
    total_comments: int
    illust_ai_type: int
    illust_book_style: int
    comment_access_control: int
