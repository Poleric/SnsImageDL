import re
from .exceptions import ExtractorError
from .twitter import TWITTER_REGEX, save_tweet_media
from .pixiv import PIXIV_REGEX, save_pixiv_media


class NotValidQuery(ExtractorError):
    pass


def save_media(query: str, **kwargs) -> None:
    """
    Uses the correct extractor and saves the specified query / url.

    Args:
        query: The url containing medias to be saved. Supported sites are: Twitter, Pixiv.

        kwargs:
            twitter_out_dir: The directory to save Twitter media. Defaults to "./twitter_media"
            pixiv_out_dir: The directory to save Pixiv media. Defaults to "./pixiv_media"

    Raises:
        NotValidQuery: Raised when specified query is not in the supported sites.
        ScrapingException: Raised when an exception is raised while parsing and saving a media.
    """

    if re.match(TWITTER_REGEX, query):
        return save_tweet_media(query, **kwargs)
    if re.match(PIXIV_REGEX, query):
        return save_pixiv_media(query, **kwargs)
    raise NotValidQuery("The specified query type is not supported.")
