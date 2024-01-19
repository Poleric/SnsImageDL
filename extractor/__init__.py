from extractor.exceptions import ExtractorError
from extractor.base import Extractor
from extractor.twitter import Twitter
from extractor.pixiv import Pixiv
from extractor.dcinside import Dcinside

from typing import Type


extractors: tuple[Type[Extractor], ...] = (
    Twitter,
    Pixiv,
    Twitter
)


class NotValidQuery(ExtractorError):
    pass


async def save_media(query: str) -> None:
    """
    Uses the correct extractor and saves the specified query / url.

    Args:
        query: The url containing medias to be saved. Supported sites are: Twitter, Pixiv, dcinside.

    Raises:
        NotValidQuery: Raised when specified query is not in the supported sites.
        ScrapingException: Raised when an exception is raised while parsing and saving a media.
    """

    for extractor in extractors:
        if extractor.check_link(query):
            async with extractor() as source:
                await source.save(query)
            return

    raise NotValidQuery("The specified query type is not supported.")
