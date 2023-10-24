import aiohttp
import re
import logging
import os
from urllib.parse import urlparse

from extractor.exceptions import MediaNotFound, InvalidLink
from extractor.utils import download_source_url

from aiohttp import ClientSession
from typing import Union, Iterable
from os import PathLike
PathLike = Union[str, bytes, PathLike]


class NotTwitterLink(InvalidLink):
    pass


class TweetDeleted(MediaNotFound):
    pass


logger = logging.getLogger(__name__)
TWITTER_REGEX = r"https://.*(?:twitter|x).com/.+/status/([0-9]+)"
HEADERS = {
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


def get_tweet_id(url: str) -> str:
    res = re.search(TWITTER_REGEX, url)
    if not res:
        raise NotTwitterLink(f"{url} is not a Twitter link.")
    return res[1]


def get_media_urls_from_embed_json(data: dict) -> Iterable[str]:
    has_media = False

    # a media can have both images and videos
    if data.get("photos"):
        has_media = True
        yield from (f'{photo["url"]}?name=large' for photo in data["photos"])

    if data.get("video"):
        has_media = True
        yield from (video["src"] for video in data["video"]["variants"])

    if not has_media:
        raise MediaNotFound


async def fetch_tweet_embed(session: ClientSession, url: str) -> dict:
    """Read tweets data. Returns a json dictionary with tweet attachment data."""
    # isolate id from url
    tweet_id = get_tweet_id(url)
    params = {
        "id": tweet_id,
        "lang": "en",
        "token": 0
    }
    async with session.get("https://cdn.syndication.twimg.com/tweet-result", headers=HEADERS, params=params) as res:
        res.raise_for_status()
        return await res.json()


async def save_tweet_media(url: str, out_dir: PathLike = "./twitter_media") -> list[str]:
    os.makedirs(out_dir, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        data = await fetch_tweet_embed(session, url)

        if data["__typename"] == "TweetTombstone":
            raise TweetDeleted(data["tombstone"]["text"]["text"])

        paths = []
        for media_url in get_media_urls_from_embed_json(data):
            try:
                filename = urlparse(media_url).path.rsplit("/", 1)[-1]  # file name already have extension
                paths.append(
                    await download_source_url(session, media_url, out_dir=out_dir, filename=filename, file_ext=None)
                )
            except aiohttp.ClientResponseError:
                logger.exception(f"Error encountered when downloading {media_url}")
        return paths


if __name__ == "__main__":
    import asyncio
    asyncio.run(save_tweet_media("https://twitter.com/hagoonha/status/1696463808259342624"))
