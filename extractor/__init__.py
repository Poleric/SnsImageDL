import re
from extractor.exceptions import ExtractorError
from extractor.twitter import TWITTER_REGEX, save_tweet_media
from extractor.pixiv import PIXIV_REGEX, save_pixiv_media
from extractor.dcinside import DCINSIDE_REGEX, save_dcinside_media


class NotValidQuery(ExtractorError):
    pass


def save_media(query: str, *, use_twitter=True, use_pixiv=True, use_dcinside=True, **kwargs) -> None:
    """
    Uses the correct extractor and saves the specified query / url.

    Args:
        query: The url containing medias to be saved. Supported sites are: Twitter, Pixiv.
        use_twitter:
        use_pixiv:
        use_dcinside:

        kwargs:
            twitter_out_dir: The directory to save Twitter media. Defaults to "./twitter_media"
            pixiv_out_dir: The directory to save Pixiv media. Defaults to "./pixiv_media"

    Raises:
        NotValidQuery: Raised when specified query is not in the supported sites.
        ScrapingException: Raised when an exception is raised while parsing and saving a media.
    """

    if use_twitter and re.match(TWITTER_REGEX, query):
        return save_tweet_media(query, **kwargs)
    if use_pixiv and re.match(PIXIV_REGEX, query):
        return save_pixiv_media(query, **kwargs)
    if use_dcinside and re.match(DCINSIDE_REGEX, query):
        return save_dcinside_media(query, **kwargs)
    raise NotValidQuery("The specified query type is not supported.")
