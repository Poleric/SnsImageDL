__all__ = (
    "UnsupportedLink",
    "AgeRestricted",
    "MediaDeleted"
)


class UnsupportedLink(ValueError):
    pass


class AgeRestricted(Exception):
    pass


class MediaDeleted(Exception):
    pass