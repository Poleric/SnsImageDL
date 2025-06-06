import logging
import re
from typing import override, AsyncGenerator

import aiohttp
import msgspec
from yarl import URL

from sns_image_dl.exceptions import UnsupportedLink, AgeRestricted, MediaDeleted
from sns_image_dl.extractor.extractor import Extractor
from sns_image_dl.extractor.twitter.models import *
from sns_image_dl.media import Media
from sns_image_dl.metadata import Metadata

__all__ = (
    "Twitter",
)

logger = logging.getLogger(__name__)


class Twitter(Extractor):
    URL_REGEX: re.Pattern = re.compile(r"https://.*(?:twitter|x).com/.+/status/([0-9]+)")

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    @override
    def is_link_supported(self, url: str) -> bool:
        return bool(self.URL_REGEX.match(url))

    def _get_tweet_id(self, url: str) -> str:
        """Extracts the tweet id from the url.

        https://x.com/<user>/status/<tweet id>  ->  <tweet id>
        """
        res = self.URL_REGEX.search(url)
        if not res:
            raise UnsupportedLink(f"{url} is not a Twitter / X link.")
        return res[1]

    async def _fetch(self, tweet_id: str) -> Tweet:
        params = {
            "id": tweet_id,
            "token": 0  # any value
        }
        cookies = {
            "auth_token": ""
        }
        async with self.session.get(
                "https://cdn.syndication.twimg.com/tweet-result",
                params=params,
                cookies=cookies
        ) as res:
            res.raise_for_status()

            tweet = msgspec.json.decode(
                await res.content.read(),
                type=Tweet | TweetTombstone,
                strict=False
            )

            if isinstance(tweet, TweetTombstone):
                match tweet.tombstone.text:  # noqa, weird code unreachable thing
                    case AgeRestrictedTombstone():
                        raise AgeRestricted
                    case PostDeletedTombstone():
                        raise MediaDeleted
                    case _:
                        logger.error(f"Unrecognizeable tweet data. Raw dump: {msgspec.json.encode(tweet)}")
                        raise Exception

            return tweet

    @staticmethod
    def _get_best_source_url(media: MediaDetails) -> str:
        def get_best_source_image_url(media: PhotoMediaDetails) -> str:
            # twitter have weird way of serving image sizes.
            # an image is usually given 4 predefined size, large, medium, small, and thumb.
            # for image that is < 2048 x 2048
            #     - the `large` size is the best quality (append `?name=large` to end of url)
            # else
            #     - the largest size is n x n where n is a power of 2 bigger than max(height, width)
            #       (append `?name=nxn` where n is ...)
            if media.sizes.large.w >= media.original_info.width \
                    and media.sizes.large.h >= media.original_info.height:
                return media.media_url_https + "?name=large"
            else:
                max_size = max(media.original_info.width, media.original_info.height)
                # https://stackoverflow.com/questions/14267555/find-the-smallest-power-of-2-greater-than-or-equal-to-n-in-python
                n = 1 << (max_size - 1).bit_length()
                return media.media_url_https + f"?name={n}x{n}"

        match media:  # noqa
            case PhotoMediaDetails():
                return get_best_source_image_url(media)
            case VideoMediaDetails() | AnimatedGifMediaDetails():
                return media.video_info.variants[-1].url
            case _:
                logger.error(f"Unsupported media type. Raw dump: {msgspec.json.encode(media)}")
                raise NotImplementedError

    @override
    async def extract(self, url: str) -> AsyncGenerator[Media, None]:  # noqa
        tweet_id = self._get_tweet_id(url)  # checks for link supported as well

        tweet = await self._fetch(tweet_id)
        for media in tweet.mediaDetails:
            source_url = self._get_best_source_url(media)
            metadata: Metadata = {
                "filename": URL(source_url).name,
                "description": tweet.text,
                "webpage_url": url,
                "source_url": source_url,
                "created_at": tweet.created_at,
                "artist": {
                    "handle": tweet.user.screen_name,
                    "display_name": tweet.user.name,
                    "webpage_url": f"https://x.com/{tweet.user.screen_name}"
                },
                "keywords": [hashtag.text for hashtag in tweet.entities.hashtags]
            }

            async with self.session.get(source_url) as res:
                yield Media(await res.content.read(), metadata)
