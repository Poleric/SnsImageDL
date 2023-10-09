import requests
import re
import logging
import os
from urllib.parse import urlparse

from extractor.exceptions import ExtractorError, MediaNotFound
from extractor.utils import download_source_url

from typing import Union, Iterable
from os import PathLike
PathLike = Union[str, bytes, PathLike]


class NotATwitterLink(ExtractorError):
    pass


class TweetDeleted(MediaNotFound):
    pass


logger = logging.getLogger(__name__)
TWITTER_REGEX = r"https://.*(?:twitter|x).com/.+/status/([0-9]+)"


def get_tweet_id(url: str) -> str:
    res = re.search(TWITTER_REGEX, url)
    if not res:
        raise NotATwitterLink(f"{url} is not a Twitter link.")
    return res[1]


def get_media_urls_from_embed_json(data: dict) -> Iterable[str]:
    if data.get("photos"):
        yield from (f'{photo["url"]}?name=large' for photo in data["photos"])
    if data.get("video"):
        yield from (video["src"] for video in data["video"]["variants"])
    if not data.get("photos") and not data.get("video"):
        raise MediaNotFound(f"Media not found for tweet id {data['id_str']}")


def get_tweet_embed_json(url: str) -> dict:
    """Read tweets data. Returns a dictionary with tweet attachment data."""
    # isolate ids from urls

    tweet_id = get_tweet_id(url)
    params = {
        "id": tweet_id,
        "lang": "en",
        "token": 0
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://platform.twitter.com",
        "Connection": "keep-alive",
        "Referer": "https://platform.twitter.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers"
    }
    ret = requests.get("https://cdn.syndication.twimg.com/tweet-result", headers=headers, params=params)
    ret.raise_for_status()

    data = ret.json()  # embed data json

    return data


def save_tweet_media(url: str, out_dir: PathLike = "./twitter_media") -> None:
    os.makedirs(out_dir, exist_ok=True)

    data = get_tweet_embed_json(url)

    if data["__typename"] == "TweetTombstone":
        raise TweetDeleted(data["tombstone"]["text"]["text"])

    for media_url in get_media_urls_from_embed_json(data):
        try:
            filename = urlparse(media_url).path.rsplit("/", 1)[-1]
            download_source_url(media_url, out_dir=out_dir, file_name=filename, file_ext="")
        except requests.exceptions.RequestException:
            logger.exception(f"Error encountered when downloading {media_url}")


if __name__ == "__main__":
    save_tweet_media("https://twitter.com/hagoonha/status/1696463808259342624")
