from typing import TypedDict, Sequence, Literal, NotRequired

type UrlLike = str


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
    type: Literal["video", "animated_gif"]
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


class TwitterTombstoneEntitiesRef(TypedDict):
    __typename: str
    url: UrlLike
    url_type: str


class TwitterTombstoneEntities(TypedDict):
    from_index: int
    to_index: int
    ref: TwitterTombstoneEntitiesRef


class TwitterTombstoneDetailsDetails(TypedDict):
    text: str  # reason
    entities: Sequence
    rtl: bool


class TwitterTombstoneDetails(TypedDict):
    text: TwitterTombstoneDetailsDetails


class TwitterTombstone(TypedDict):
    __typename: Literal["TweetTombstone"]
    tombstone: TwitterTombstoneDetails


class TwitterEmbedDetails(TypedDict):
    __typename: Literal["Tweet"]
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
