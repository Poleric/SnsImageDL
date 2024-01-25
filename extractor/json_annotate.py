from typing import Sequence, TypedDict, Literal, NotRequired

type UrlLike = str


"""
Pixiv
"""
class PixivImage(TypedDict, total=False):
    large: UrlLike
    medium: UrlLike
    square_medium: UrlLike
    original: UrlLike


class PixivUser(TypedDict):
    account: str  # account handle?
    id: int
    is_followed: bool
    name: str  # display name
    profile_image_urls: PixivImage


class PixivTag(TypedDict):
    name: str
    translated_name: str | None


class PixivMetaSinglePage(TypedDict):
    original_image_url: UrlLike

class PixivMetaPage(TypedDict):
    image_urls: PixivImage


class PixivIllustDetails(TypedDict):
    id: int
    title: str | Literal["無題", "no title"]  # prob more no title literals for other language, kr, zh
    type: Literal["illust", "ugoira"]
    image_urls: PixivImage
    caption: str  # description
    restrict: int
    user: PixivUser
    tags: Sequence[PixivTag]
    tools: Sequence[str]
    create_date: str  # YYYY-MM-DDTHH:mm:ss+TZ:00
    page_count: int
    width: int
    height: int
    sanity_level: int
    x_restrict: int  # sfw - 0  nsfw - 1
    series: str | None  # TODO: double check
    meta_single_page: PixivMetaSinglePage  # check
    meta_pages: Sequence[PixivMetaPage]
    total_view: int
    total_bookmarks: int
    is_bookmarked: bool
    visible: bool
    is_muted: bool
    total_comments: int
    illust_ai_type: int
    illust_book_style: int
    comment_access_control: int


"""
Twitter
"""
class TwitterHashtag(TypedDict):
    indices: tuple[int, int]
    text: str


class TwitterMediaEntity(TypedDict):
    display_url: UrlLike  # short url?
    expanded_url: UrlLike  # original url + /photo/{number}
    indices: tuple[int, int]
    url: UrlLike  # shortest url


class TwitterEntities(TypedDict):
    hashtags: Sequence[TwitterHashtag]
    urls: Sequence  # TODO: find out
    user_mentions: Sequence  # TODO: find out
    symbols: Sequence  # TODO: find out
    media: Sequence[TwitterMediaEntity]


class TwitterUser(TypedDict):
    id_str: str  # user id
    name: str  # twitter handle
    profile_image_url_https: UrlLike
    screen_name: str  # display name
    verified: bool
    is_blue_verified: bool
    profile_image_shape: Literal["Circle"]  # the nft thing?  TODO: find a special shape


class TwitterEditControl(TypedDict):
    edit_tweet_ids: Sequence[str]  # would assume with edit perms
    editable_until_msecs: str
    is_edit_eligible: bool
    edits_remaining: str


class TwitterImageRegion(TypedDict):
    x: int
    y: int
    w: int
    h: int


class TwitterOriginalMediaInfo(TypedDict):
    height: int
    width: int
    focus_rects: Sequence[TwitterImageRegion]


class TwitterMediaSize(TypedDict):
    h: int
    resize: Literal["fit", "crop"]  # TODO: double check
    w: int


class TwitterMediaSizeInfo(TypedDict):
    large: TwitterMediaSize
    medium: TwitterMediaSize
    small: TwitterMediaSize
    thumb: TwitterMediaSize


class TwitterMediaAvailability(TypedDict):
    status: Literal["Available"]  # TODO: check more


class TwitterMediaDetails(TypedDict):
    display_url: UrlLike
    expanded_url: UrlLike
    ext_media_availability: TwitterMediaAvailability
    indices: tuple[int, int]
    media_url_https: UrlLike  # media base url
    original_info: TwitterOriginalMediaInfo
    sizes: TwitterMediaSizeInfo
    type: Literal["photo", "video"]  # TODO: double check


class TwitterVideoInfoVariant(TypedDict):
    bitrate: NotRequired[int]
    content_type: Literal["video/mp4", "application/x-mpegURL"]
    url: UrlLike


class TwitterVideoInfo(TypedDict):
    aspect_ratio: tuple[int, int]
    duration_millis: int
    variants: Sequence[TwitterVideoInfoVariant]


class TwitterMediaDetailsVideo(TwitterMediaDetails):
    additional_media_info: dict
    type: Literal["video"]
    video_info: TwitterVideoInfo


class TwitterRGBDetails(TypedDict):
    red: int
    green: int
    blue: int


class TwitterPhotoDetails(TypedDict):
    backgroundColor: TwitterRGBDetails
    cropCandidates: Sequence[TwitterImageRegion]
    expandedUrl: UrlLike
    url: UrlLike  # source base url
    width: int
    height: int


class TwitterVideoVariantDetails(TypedDict):
    type: Literal["video/mp4", "application/x-mpegURL"]  # TODO: research more
    src: UrlLike


class TwitterVideoIdDetails(TypedDict):
    type: Literal["tweet"]  # TODO: research more
    id: str


class TwitterVideoDetails(TypedDict):
    aspectRatio: tuple[int, int]
    contentType: Literal["media_entity"]  # TODO: research more
    durationMs: int
    mediaAvailability: TwitterMediaAvailability
    poster: UrlLike  # thumbnail
    variants: Sequence[TwitterVideoVariantDetails]
    videoId: TwitterVideoIdDetails
    viewCount: int


class TwitterEmbedDetails(TypedDict):
    __typename: Literal["Tweet", "TweetTombstone"]
    lang: str
    favorite_count: int
    possibly_sensitive: bool
    created_at: str  # YYYY-MM-DDTHH:mm:ss.sssZ
    display_text_range: tuple[int, int]
    entities: TwitterEntities
    id_str: str   # tweet id
    text: str  # tweet text
    user: TwitterUser
    edit_control: TwitterEditControl
    mediaDetails: Sequence[TwitterMediaDetails | TwitterMediaDetailsVideo]
    photos: Sequence[TwitterPhotoDetails]
    video: NotRequired[TwitterVideoDetails]
    conversation_count: int
    news_action_type: Literal["conversation"]  # TODO: do more research
    isEdited: bool
    isStaleEdit: bool
