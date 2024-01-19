import re
import os
import aiohttp
from urllib.parse import urlparse
from extractor.base import Extractor, UrlLike, PathLike
from extractor.exceptions import MediaNotFound, InvalidLink, SessionNotCreated

from typing import Iterable
# from typing import override


class NotTwitterLink(InvalidLink):
    pass


class TweetDeleted(MediaNotFound):
    pass


class Twitter(Extractor):
    SITE_REGEX = r"https://.*(?:twitter|x).com/.+/status/([0-9]+)"
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

    # @override   # py 3.12 stuff
    def __str__(self):
        return "Twitter"

    # @override
    async def save(self, webpage_url: UrlLike, output_directory: PathLike = "./twitter_media", filename: str = None) -> None:
        if not self.session:
            raise SessionNotCreated("Session is not initialized fully. Use a context manager when saving.")

        media_urls = list(await self.get_media_urls(webpage_url))

        if not media_urls:
            raise MediaNotFound

        os.makedirs(output_directory, exist_ok=True)
        for media_url in media_urls:
            try:
                async with self.session.get(media_url, headers=self.HEADERS) as res:
                    content = await res.content.read()
            except aiohttp.ClientResponseError:
                self.logger.exception(f"Error encountered when downloading {media_url}")
            else:
                filename = self.get_filename(media_url)
                if not self.have_file_extension(filename):
                    filename = filename + "." + self.guess_file_extension(content)

                self.save_to(content, output_directory, filename)

    async def get_media_urls(self, webpage_url: UrlLike) -> Iterable[UrlLike]:
        return self.get_media_urls_from_embed_json(
            await self.fetch_tweet_embed(webpage_url)
        )

    # Twitter implementation
    def get_tweet_id(self, webpage_url: UrlLike) -> str:
        res = re.search(self.SITE_REGEX, webpage_url)
        if not res:
            raise NotTwitterLink(f"{webpage_url} is not a Twitter link.")
        return res[1]

    @staticmethod
    def get_media_urls_from_embed_json(data: dict) -> Iterable[UrlLike]:
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

    async def fetch_tweet_embed(self, webpage_url: UrlLike) -> dict:
        """Read tweets data. Returns a json dictionary with tweet attachment data."""
        # isolate id from url
        tweet_id = self.get_tweet_id(webpage_url)
        params = {
            "id": tweet_id,
            "lang": "en",
            "token": 0
        }
        async with self.session.get(
            "https://cdn.syndication.twimg.com/tweet-result",
            headers=self.HEADERS,
            params=params
        ) as res:
            res.raise_for_status()
            return await res.json()

    @staticmethod
    def get_filename(source_url: UrlLike):
        return urlparse(source_url).path.rsplit("/", 1)[-1]


if __name__ == "__main__":
    import asyncio
    link = "https://twitter.com/hagoonha/status/1696463808259342624"

    async def main():
        async with Twitter() as twitter:
            await twitter.save(link)

    asyncio.run(main())
