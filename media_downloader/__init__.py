from .exceptions import ExtractorError
from .base import Extractor
from .twitter import Twitter
from media_downloader.pixiv.pixiv import Pixiv
from .dcinside import Dcinside
from .media import Media

from typing import Type


extractors: tuple[Type[Extractor], ...] = (
    Twitter,
    Pixiv,
    Dcinside
)


class NotValidQuery(ExtractorError):
    pass


def get_matching_extractor(query: str) -> Type[Extractor] | None:
    for extractor in extractors:
        if extractor.check_link(query):
            return extractor


async def save_media(query: str) -> None:
    """
    Uses the correct extractor and saves the specified query / url.

    Args:
        query: The url containing medias to be saved. Supported sites are: Twitter, Pixiv, dcinside.

    Raises:
        NotValidQuery: Raised when specified query is not in the supported sites.
        ScrapingException: Raised when an exception is raised while parsing and saving a media.
    """

    extractor = get_matching_extractor(query)

    if extractor is None:
        raise NotValidQuery("The specified query type is not supported.")

    async with extractor() as extractor:
        async for media in extractor.get_all_media(query):
            media.save(f"./saved_media/{extractor.__class__.__name__.casefold()}_media/")


