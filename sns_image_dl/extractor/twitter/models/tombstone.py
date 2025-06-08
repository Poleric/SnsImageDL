##########################
# Twitter CDN API Schema #
##########################
from typing import ClassVar

from msgspec import Struct

from sns_image_dl.extractor.twitter.models.base import TweetResponse

__all__ = (
    "EntityReference",
    "TombstoneEntities",
    "TombstoneDetails",
    "Tombstone",
    "TweetTombstone",
)


class EntityReference(Struct):
    __typename: str
    url: str
    url_type: str


class TombstoneEntities(Struct):
    from_index: int
    to_index: int
    ref: EntityReference


class TombstoneDetails(Struct):
    text: str
    entities: list[TombstoneEntities]
    rtl: bool

    AgeRestrictedText: ClassVar[str] = \
        "Age-restricted adult content. This content might not be appropriate for people under 18 years old. To view this media, you’ll need to log in to X. Learn more"
    PostDeletedText: ClassVar[str] = "This Post was deleted by the Post author. Learn more"


class Tombstone(Struct):
    text: TombstoneDetails


class TweetTombstone(TweetResponse):
    tombstone: Tombstone
