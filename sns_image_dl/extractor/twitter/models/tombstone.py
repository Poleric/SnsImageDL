##########################
# Twitter CDN API Schema #
##########################
from msgspec import Struct

from sns_image_dl.extractor.twitter.models.base import TweetResponse

__all__ = (
    "TweetTombstone",
    "AgeRestrictedTombstone",
    "PostDeletedTombstone"
)


class EntityReference(Struct):
    __typename: str
    url: str
    url_type: str


class TombstoneEntities(Struct):
    from_index: int
    to_index: int
    ref: EntityReference


class TombstoneDetails(Struct, tag_field="text"):
    entities: list[TombstoneEntities]
    rtl: bool


class AgeRestrictedTombstone(TombstoneDetails,
                             tag="Age-restricted adult content. This content might not be appropriate for people under 18 years old. To view this media, you’ll need to log in to X. Learn more"):
    pass


class PostDeletedTombstone(TombstoneDetails, tag="This Post was deleted by the Post author. Learn more"):
    pass


class Tombstone(Struct):
    text: AgeRestrictedTombstone | PostDeletedTombstone


class TweetTombstone(TweetResponse):
    tombstone: Tombstone
