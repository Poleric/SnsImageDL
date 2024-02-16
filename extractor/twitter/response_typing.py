from typing import TypedDict, Literal, NotRequired

type UrlLike = str
type Range = tuple[int, int]
type AspectRatio = tuple[int, int]


class BadRequestResponse(TypedDict):
    error: Literal["Bad request."]


class AgeRestrictedResponse(TypedDict):
    class Tombstone(TypedDict):
        class Tombstone(TypedDict):
            class TombstoneEntities(TypedDict):
                class Reference(TypedDict):
                    __typename: str
                    url: UrlLike
                    url_type: str

                from_index: int
                to_index: int
                ref: Reference

            text: Literal["Age-restricted adult content. This content might not be appropriate for people under 18 years old. To view this media, you’ll need to log in to X. Learn more"]
            entities: list[TombstoneEntities]
            rtl: bool

        text: Tombstone

    __typename: Literal["TweetTombstone"]
    tombstone: Tombstone


class TweetDeletedResponse(TypedDict):
    class Tombstone(TypedDict):
        class Tombstone(TypedDict):
            class TombstoneEntities(TypedDict):
                class Reference(TypedDict):
                    __typename: str
                    url: UrlLike
                    url_type: str

                from_index: int
                to_index: int
                ref: Reference

            text: Literal["This Post was deleted by the Post author. Learn more"]
            entities: list[TombstoneEntities]
            rtl: bool

        text: Tombstone

    __typename: Literal["TweetTombstone"]
    tombstone: Tombstone


class TweetResponse(TypedDict):
    class EntitiesList(TypedDict):
        class HashtagEntity(TypedDict):
            indices: Range  # the location of the hashtag in the tweet content
            text: str

        class UserMentionEntity(TypedDict):
            id_str: str       # user id
            indices: Range
            name: str         # twitter display name
            screen_name: str  # username

        class MediaEntity(TypedDict):
            display_url: UrlLike   # shortened url, "pic.twitter.com/<same id>"
            expanded_url: UrlLike  # original url
            indices: Range
            url: UrlLike           # shortened url, "https://t.co/<same id>"

        hashtags: list[HashtagEntity]
        urls: list
        user_mentions: list[UserMentionEntity]
        symbols: list
        media: list[MediaEntity]

    class User(TypedDict):
        id_str: str                       # user id
        name:  str                        # display name
        profile_image_url_https: UrlLike  # pfp image url
        screen_name: str                  # username
        verified: bool
        verified_type: NotRequired[str]  # only seen "Business"
        is_blue_verified: bool
        profile_image_shape: Literal["Circle", "Square"]

    class EditControl(TypedDict):
        edit_tweet_ids: list[str]
        editable_until_msecs: str  # unix timestamp
        is_edit_eligible: bool
        edits_remaining: str       # is int

    class MediaDetail(TypedDict):
        class MediaAvailability(TypedDict):
            status: str

        class MediaInfo(TypedDict):
            class Area(TypedDict):
                x: int
                y: int
                w: int
                h: int

            height: int
            width: int
            focus_rects: list[Area]

        class MediaSizes(TypedDict):
            class Size(TypedDict):
                h: int
                resize: Literal["fit", "crop"]
                w: int

            large: Size
            medium: Size
            small: Size
            thumb: Size

        class VideoInfo(TypedDict):
            class VideoVariant(TypedDict):
                bitrate: int
                content_type: str  # <type>/<ext>
                url: UrlLike

            aspect_ratio: AspectRatio
            duration_millis: int
            variants: list[VideoVariant]

        display_url: UrlLike      # shortened url, "pic.twitter.com/<same id>"
        expanded_url: UrlLike     # original url
        ext_media_availability: MediaAvailability
        indices: Range
        media_url_https: UrlLike  # image source url
        original_info: MediaInfo
        sizes: MediaSizes
        type: Literal["photo", "video", "animated_gif"]
        url: UrlLike              # shortened url, "https://t.co/<same id>"
        video_info: NotRequired[VideoInfo]

    class Photo(TypedDict):
        class RGB(TypedDict):
            red: int
            green: int
            blue: int

        class Area(TypedDict):
            x: int
            y: int
            w: int
            h: int

        backgroundColor: RGB
        cropCandidates: list[Area]
        expandedUrl: UrlLike  # tweet url
        url: UrlLike          # image source url
        width: int
        height: int

    class Video(TypedDict):
        class MediaAvailability(TypedDict):
            status: str

        class VideoVariant(TypedDict):
            type: str  # <type>/<extension>
            src: UrlLike  # media source

        class VideoId(TypedDict):
            type: Literal["tweet"]
            id: str

        aspectRatio: AspectRatio
        contentType: str              # only seen "media_entity"
        durationMs: int
        mediaAvailability: MediaAvailability
        poster: UrlLike               # thumbnail
        variants: list[VideoVariant]  # usually last entry have best quality
        videoId: VideoId
        viewCount: int

    __typename: Literal["Tweet"]
    lang: str
    favorite_count: int        # like count
    possibly_sensitive: int    # age restricted?
    created_at: str            # datetime, YYYY-MM-DDTHH:mm:ss.fffZ
    display_text_range: Range  # tweet length
    entities: EntitiesList
    id_str: str                # tweet id
    text: str                  # tweet content
    user: User
    edit_control: EditControl
    mediaDetails: list[MediaDetail]
    photos: list[Photo]  # usually not best quality
    videos: Video
    conversation_count: int  # comments
    news_action_type: str  # so "conversation"
    isEdited: bool
    isStaleEdit: bool
