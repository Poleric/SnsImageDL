##########################
# Twitter CDN API Schema #
##########################
from datetime import datetime
from typing import Literal

from msgspec import Struct

from snsimagedl_twitter.models.base import TweetResponse

__all__ = (
    "Tweet",
    "MediaDetails",
    "PhotoMediaDetails",
    "VideoMediaDetails",
    "AnimatedGifMediaDetails"
)

type Range = tuple[int, int]


class Area(Struct):
    x: int
    y: int
    w: int
    h: int


class MediaAvailability(Struct):
    status: Literal["Available"]


class EntitiesList(Struct):
    class HashtagEntity(Struct):
        indices: Range  # the location of the hashtag in the tweet content
        text: str

    class UserMentionEntity(Struct):
        id_str: str  # user id
        indices: Range
        name: str  # twitter display name
        screen_name: str  # username

    class MediaEntity(Struct):
        display_url: str  # shortened url, "pic.twitter.com/<same id>"
        expanded_url: str  # original url
        indices: Range
        url: str  # shortened url, "https://t.co/<same id>"

    hashtags: list[HashtagEntity]
    urls: list
    user_mentions: list[UserMentionEntity]
    symbols: list
    media: list[MediaEntity]


class User(Struct, kw_only=True):
    id_str: str  # user id
    name: str  # display name
    profile_image_url_https: str  # pfp image url
    screen_name: str  # user handle
    verified: bool
    verified_type: str | None = None  # only seen "Business"
    is_blue_verified: bool
    profile_image_shape: Literal["Circle", "Square"]


class EditControl(Struct):
    edit_tweet_ids: list[str]
    editable_until_msecs: int  # unix timestamp in millis, whole number
    is_edit_eligible: bool
    edits_remaining: int


class VideoInfo(Struct):
    class VideoVariant(Struct):
        bitrate: int
        content_type: str  # MIME types https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/MIME_types/Common_types
        url: str

    aspect_ratio: tuple[int, int]
    duration_millis: int
    variants: list[VideoVariant]


class MediaDetails(Struct, tag_field="type"):
    class MediaInfo(Struct):
        height: int
        width: int
        focus_rects: list[Area]

    class MediaSizes(Struct):
        class Size(Struct):
            h: int
            w: int
            resize: Literal["fit", "crop"]

        large: Size
        medium: Size
        small: Size
        thumb: Size

    display_url: str  # shortened url, "pic.twitter.com/<same id>"
    expanded_url: str  # original url
    ext_media_availability: MediaAvailability
    indices: Range
    media_url_https: str  # image source url
    original_info: MediaInfo
    sizes: MediaSizes
    url: str  # shortened url, "https://t.co/<same id>"


class PhotoMediaDetails(MediaDetails, tag="photo"):
    pass


class VideoMediaDetails(MediaDetails, tag="video"):
    video_info: VideoInfo


class AnimatedGifMediaDetails(MediaDetails, tag="animated_gif"):
    video_info: VideoInfo


class Photo(Struct):
    class RGB(Struct):
        red: int
        green: int
        blue: int

    backgroundColor: RGB
    cropCandidates: list[Area]
    expandedUrl: str  # tweet url
    url: str  # image source url
    width: int
    height: int


class Video(Struct):
    class VideoVariant(Struct):
        content_type: str  # MIME types https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/MIME_types/Common_types
        url: str

    class VideoId(Struct):
        type: Literal["tweet"]
        id: str

    aspectRatio: tuple[int, int]
    contentType: str  # only seen "media_entity"
    durationMs: int
    mediaAvailability: MediaAvailability
    poster: str  # thumbnail url
    variants: list[VideoVariant]  # usually last entry have the best quality
    videoId: VideoId
    viewCount: int


class Tweet(TweetResponse):
    lang: str
    favorite_count: int  # like count
    possibly_sensitive: bool  # is age restricted
    created_at: datetime  # datetime, YYYY-MM-DDTHH:mm:ss.fffZ
    display_text_range: Range  # tweet length
    entities: EntitiesList
    id_str: str  # tweet id
    text: str  # tweet content
    user: User
    edit_control: EditControl
    mediaDetails: list[PhotoMediaDetails | VideoMediaDetails | AnimatedGifMediaDetails]
    photos: list[Photo]
    conversation_count: int  # comments
    news_action_type: str  # values = ["conversation"]
    isEdited: bool
    isStaleEdit: bool
    videos: Video | None = None
