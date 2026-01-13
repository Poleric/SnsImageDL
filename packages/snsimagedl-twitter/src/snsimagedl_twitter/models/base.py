from msgspec import Struct

__all__ = (
    "TweetResponse",
)


class TweetResponse(Struct, tag=True, tag_field="__typename"):
    pass
