from pixivpy3 import *
from pixivpy3.utils import PixivError
import re
import os
import logging
import sys

from extractor.exceptions import MediaNotFound

from typing import Union
from os import PathLike
PathLike = Union[str, bytes, PathLike]


logger = logging.getLogger(__name__)
PIXIV_REGEX = r"https://www.p.?ixiv.net/en/artworks/([0-9]+)"
_pixiv_api = None
REFRESH_TOKEN = os.getenv("PIXIV_REFRESH_TOKEN")
if not REFRESH_TOKEN:
    logging.exception("PIXIV_REFRESH_TOKEN is required. Refer to https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362 to get your refresh token and add it into the environment variable with the name PIXIV_REFRESH_TOKEN")
    sys.exit()


def get_global_pixiv() -> AppPixivAPI:
    global _pixiv_api
    if not _pixiv_api:  # login
        _pixiv_api = AppPixivAPI(timeout=3)
        _pixiv_api.auth(refresh_token=REFRESH_TOKEN)

    return _pixiv_api


def get_pixiv_id(url: str) -> str:
    res = re.search(PIXIV_REGEX, url)
    assert res, f"{url} is not a Pixiv url"
    return res[1]


def get_pixiv_illust(url: str) -> dict:
    # tries 3 times
    api = get_global_pixiv()
    for i in range(3):
        json_result = api.illust_detail(get_pixiv_id(url))
        if "error" in json_result and "invalid_grant" in json_result["error"]["message"]:
            api.auth()
            continue
        return json_result.illust

    # if no results
    raise PixivError(f"Error in retrieving {url} data")


def get_pixiv_media_urls(data: dict) -> list[str]:
    urls = []

    # is illustration
    if data["type"] == "illust":
        if data["meta_pages"]:  # for multiple images stuff
            for page in data["meta_pages"]:
                urls.append(page["image_urls"]["original"])
        else:
            urls.append(data["meta_single_page"]["original_image_url"])
    # is animation
    elif data["type"] == "ugoira":
        # TODO: related issues: https://github.com/upbit/pixivpy/issues/164, https://github.com/upbit/pixivpy/issues/253
        raise NotImplemented("Ugoira is a bit iffy to make. will do sometime")
    # is nothing
    else:
        raise MediaNotFound

    return urls


def save_pixiv_media(url, out_dir: PathLike = "./pixiv_media"):
    os.makedirs(out_dir, exist_ok=True)

    illust = get_pixiv_illust(url)
    img_urls = get_pixiv_media_urls(illust)

    api = get_global_pixiv()
    # tries 3 times
    for img_url in img_urls:
        for i in range(3):
            try:
                if api.download(img_url, path=out_dir):
                    pass
                break
            except PixivError:
                logging.exception(f"Download {url} failed.")


if __name__ == "__main__":
    urls = [
        "https://www.pixiv.net/en/artworks/97138089",
        "https://www.pixiv.net/en/artworks/92217855",
        "https://www.pixiv.net/en/artworks/99875723",
        "https://www.pixiv.net/en/artworks/96398887",
    ]

    for url in urls:
        save_pixiv_media(url, out_dir="./pixiv_img")
