import requests
import re
import logging
import os
from urllib.parse import urlparse
# import io
# import math
# import string

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
TWITTER_REGEX = r"https://.*twitter.com/.+/status/([0-9]+)"

#  Twitter dont care what value the token field, as long it exists.
#
# CHARACTERS = string.digits + string.ascii_lowercase
# def v8_float_to_radix(number: float, radix: int, significant_figures: int = 11) -> str:
#     """https://github.com/v8/v8/blob/master/src/numbers/conversions.cc#L1309-L1330"""
#
#     integral = math.floor(number)
#     fraction = number - integral
#
#     integral_builder = io.StringIO()
#     fractional_builder = io.StringIO()
#
#     # handle negative sign
#     if number < 0:
#         integral_builder.write('-')
#         number = -number
#
#     # decimal part
#     num_of_digits_of_integral_after_radix = 1 + math.floor(math.log(integral) / math.log(radix)) if integral else 0
#     sig_figs = 0
#     while fraction > 0:
#         fraction *= radix
#
#         digit = int(fraction)
#         fractional_builder.write(CHARACTERS[digit])
#         fraction -= digit
#
#         if digit != 0 or sig_figs:
#             sig_figs += 1
#
#         if sig_figs >= significant_figures - num_of_digits_of_integral_after_radix:
#             if fraction > 0.5 or (fraction == 0.5 and (digit & 1)):
#                 while True:
#                     fractional_builder.seek(fractional_builder.tell() - 1)  # move pointer back 1
#                     if fractional_builder.tell() == 0:
#                         integral += 1
#                         break
#
#                     if digit + 1 < radix:
#                         fractional_builder.write(CHARACTERS[digit + 1])
#                         break
#             break
#
#     # integer part
#     if integral == 0:
#         integral_builder.write('0')
#     else:
#         while integral > 0:
#             integral, remainder = divmod(integral, radix)
#             integral_builder.write(CHARACTERS[remainder])
#
#     # reverse order of
#     result = integral_builder.getvalue()[::-1] + '.' + fractional_builder.getvalue()
#     integral_builder.close(); fractional_builder.close()
#     return result
#
#
# def get_token(tweet_id: str) -> str:
#     """A function in Twitter js code that generates token for each tweet.
#
#     from the (obfuscated) source code:
#     Line 131 from embed.Tweet.<some_random_hash>.js (slightly modified to be easier to read)
#     s = Number
#     a = window.Math
#     o = function(e) {
#         return e.toString(Math.pow(6, 2))
#     }
#     c = function(e) {
#         return e.replace(/(0+|\.)/g, "")
#     }
#     u = function(e) {
#         this.Tweet = function(e) {
#             return {
#                 fetch: function(t, r) {
#                     return e.get("tweet-result", (0,
#                     n.Z)({}, t, {
#                         token: c(o(s(t.id) / 1e15 * a.PI))  <--- important bit
#                     }), r).then((function(e) {
#                         return e && (e.id_str || "TweetTombstone" === e.__typename) ? Promise.resolve(e) : Promise.reject(new Error("could not parse api response"))
#                     }
#                     ))
#                 }
#             }
#         }(e)
#     }
#     """
#     """
#     From the js code, it
#     1. int(tweet_id) / 10**15 * PI
#     2. base36 encodes it
#     3. remove "0" and "."
#     """
#     return re.sub(r"(0+|\.)", "", v8_float_to_radix(int(tweet_id) / 1e15 * math.pi, 36))


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


def save_tweet_media(url: str, twitter_our_dir: PathLike = "./twitter_media", **kwargs) -> None:
    os.makedirs(twitter_our_dir, exist_ok=True)

    data = get_tweet_embed_json(url)

    if data["__typename"] == "TweetTombstone":
        raise TweetDeleted(data["tombstone"]["text"]["text"])

    for media_url in get_media_urls_from_embed_json(data):
        try:
            filename = urlparse(media_url).path.rsplit("/", 1)[-1]
            download_source_url(media_url, f"{twitter_our_dir}/{filename}")
        except requests.exceptions:
            logger.exception(f"Error encountered when downloading {media_url}")


if __name__ == "__main__":
    save_tweet_media("https://twitter.com/hagoonha/status/1696463808259342624")

