import requests
import re
import logging
import os
from urllib.parse import urlparse

from .exceptions import ExtractorError, MediaNotFound
from .utils import download_source_url

from typing import Union
from os import PathLike
PathLike = Union[str, bytes, PathLike]


class NotATwitterLink(ExtractorError):
    pass


logger = logging.getLogger(__name__)
TWITTER_REGEX = r"https://.*twitter.com/.+/status/([0-9]+)"


def get_tweet_id(url: str) -> str:
    res = re.search(TWITTER_REGEX, url)
    if not res:
        raise NotATwitterLink(f"{url} is not a Twitter link.")
    return res[1]


def get_media_urls_from_embed_json(data: dict) -> list[str]:
    if data.get("photos"):
        return [f'{photo["url"]}?name=large' for photo in data["photos"]]
    elif data.get("video"):
        return [video["src"] for video in data["video"]["variants"]]
    else:
        raise MediaNotFound(f"Media not found for tweet id {data['id_str']}")


def get_tweet_embed_json(url: str) -> dict:
    """Read tweets data. Returns a dictionary with tweet attachment data."""
    # isolate ids from urls

    tweet_id = get_tweet_id(url)
    params = {
        "id": tweet_id
    }
    ret = requests.get("https://cdn.syndication.twimg.com/tweet-result", params=params)
    ret.raise_for_status()

    data = ret.json()  # embed data json

    return data


def save_tweet_media(url: str, twitter_our_dir: PathLike = "./twitter_media", **kwargs) -> None:
    data = get_tweet_embed_json(url)

    os.makedirs(twitter_our_dir, exist_ok=True)
    media_urls = get_media_urls_from_embed_json(data)

    for media_url in media_urls:
        try:
            filename = urlparse(media_url).path.rsplit("/", 1)[-1]
            download_source_url(media_url, f"{twitter_our_dir}/{filename}")
        except requests.exceptions:
            logger.exception(f"Error encountered when downloading {media_url}")

