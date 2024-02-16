import re
import math
import logging
import json
from ..extractor import Extractor, UrlLike
from ..exceptions import MediaNotFound, InvalidLink
from ..tags import Tag
from ..media import Media

from typing import Iterable, override
from .response_typing import BadRequestResponse, AgeRestrictedResponse, TweetDeletedResponse, TweetResponse
type TweetTombstone = AgeRestrictedResponse | TweetDeletedResponse
type TwitterResponse = BadRequestResponse | TweetTombstone | TweetResponse




class NotTwitterLink(InvalidLink):
    pass


class TweetDeleted(MediaNotFound):
    pass


class AgeRestricted(MediaNotFound):
    pass


def get_source_url_from_media_details(media_detail: TweetResponse.MediaDetail) -> UrlLike:
    match media_detail:
        case {"type": "photo"}:
            return get_best_quality_image_link(media_detail)
        case {"type": "video" | "animated_gif"}:
            return media_detail["video_info"]["variants"][-1]["url"]  # usually best quality
        case {"type": unknown}:
            logging.debug(
                f"Unexpected type {unknown}.\n"
                f"Full dump: {json.dumps(media_detail, indent=4)}"
            )


def get_best_quality_image_link(image_details: TweetResponse.MediaDetail) -> UrlLike:
    # twitter have weird way they keep images and in the json.
    # they store a base url of, for eg, https://pbs.twimg.com/media/<image_thing>.jpg
    # sometimes giving the args of ?name=large will give the best quality,
    # but if it is bigger than 2048 x 2048 (from small testing), ?name=large will not give the best quality
    # instead ?name=4096x4096 will yield the best quality
    # PS: currently testing if it's a best fit of pow of 2

    def get_next_pow_2(n: int) -> int:
        return 2 ** math.ceil(math.log2(n))

    large_w, large_h = image_details["sizes"]["large"]["w"], image_details["sizes"]["large"]["h"]
    original_w, original_h = image_details["original_info"]["width"], image_details["original_info"]["height"]

    if large_w >= original_w and large_h >= original_h:
        return f"{image_details['media_url_https']}?name=large"
    else:
        max_resolution = max(get_next_pow_2(original_w), get_next_pow_2(original_h))
        return f"{image_details['media_url_https']}?name={max_resolution}x{max_resolution}"


class Twitter(Extractor):
    URL_REGEX = r"https://.*(?:twitter|x).com/.+/status/([0-9]+)"
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

    @override
    async def get_all_media(self, webpage_url: UrlLike) -> Iterable[Media]:
        tweet_embed = await self.fetch_tweet(webpage_url)

        if tweet_embed["__typename"] == "TweetTombstone":
            tweet_embed: TweetTombstone
            reason = tweet_embed["tombstone"]["text"]["text"]

            if reason.startswith("Age-restricted adult content"):
                raise AgeRestricted(reason)
            elif reason.startswith("This Post was deleted"):
                raise TweetDeleted(reason)
            else:
                raise MediaNotFound(reason)

        tweet_embed: TweetResponse
        for media_details in tweet_embed["mediaDetails"]:
            source_url = get_source_url_from_media_details(media_details)
            tag: Tag = {
                "description": tweet_embed["text"],
                "webpage_url": webpage_url,
                "source_url": source_url,
                "created_at": tweet_embed["created_at"],
                "artist": {
                    "name": tweet_embed["user"]["name"],
                    "display_name": tweet_embed["user"]["screen_name"],
                    "webpage_url": f"https://twitter.com/{tweet_embed["user"]["name"]}"
                },
                "keywords": [hashtag["text"] for hashtag in tweet_embed["entities"]["hashtags"]]
            }

            async with self.session.get(source_url, headers=self.HEADERS) as res:
                media = Media(
                    content=await res.content.read(),
                    filename=self.get_url_basename(source_url),
                    tags=tag
                )
                yield media

    # Twitter implementation
    def get_tweet_id(self, webpage_url: UrlLike) -> str:
        res = re.search(self.URL_REGEX, webpage_url)
        if not res:
            raise NotTwitterLink(f"{webpage_url} is not a Twitter link.")
        return res[1]

    async def fetch_tweet(self, webpage_url: UrlLike, auth_token: str = "") -> TwitterResponse:
        """Read tweets data. Returns a json dictionary with tweet attachment data.

        :param webpage_url: any support tweet url. Includes its derivatives like fxtwitter, vxtwitter,...
        :param auth_token: the auth_token cookie on Twitter. Used for scraping age restricted content.
        """
        # isolate id from url
        tweet_id = self.get_tweet_id(webpage_url)
        params = {
            "id": tweet_id,
            "lang": "en",
            "token": 0
        }
        try:
            async with self.session.get(
                "https://cdn.syndication.twimg.com/tweet-result",
                headers=self.HEADERS,
                params=params
            ) as res:
                res.raise_for_status()
                return await res.json()
        except AgeRestricted:
            cookies = {
                "auth_token": auth_token
            }
            async with self.session.get(
                "https://cdn.syndication.twimg.com/tweet-result",
                headers=self.HEADERS,
                params=params,
                cookies=cookies
            ) as res:
                res.raise_for_status()
                return await res.json()


if __name__ == "__main__":
    import asyncio
    import os
    single_2480_3750 = "https://twitter.com/hagoonha/status/1696463808259342624"
    jp_in_username = "https://twitter.com/AZchangaa/status/1748347428242342294"
    single_video = "https://twitter.com/anzerusu/status/1748269067155165480"
    single_2220_3118 = "https://twitter.com/UshakuChen/status/1748325819498553463"
    single_1321_1045 = "https://twitter.com/hrn_ohana/status/1750496540547010566"

    async def main():
        async with Twitter() as twitter:
            os.makedirs("./twitter_media", exist_ok=True)
            async for media in twitter.get_all_media("https://twitter.com/NKNK_NGRMS/status/1741474753498497459"):
                media.save(output_directory="./twitter_media", add_metadata=True)
            # print(json.dumps(await twitter.fetch_tweet("https://twitter.com/NKNK_NGRMS/status/1741474753498497459"), indent=4))

    asyncio.run(main())
