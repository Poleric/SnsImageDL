from bs4 import BeautifulSoup
import aiohttp
import os
import logging
import re

from extractor.exceptions import MediaNotFound, InvalidLink
from extractor.utils import download_source_url

from aiohttp import ClientSession
from typing import Union, Iterable
from os import PathLike
PathLike = Union[str, bytes, PathLike]
logger = logging.getLogger(__name__)


class NotDcinsideLink(InvalidLink):
    pass


DCINSIDE_REGEX = r"https://(?:gall|m).dcinside.com/[a-zA-Z/]*(?:\?id=|(?:board|m)/)(\w+)(?:&no=|/)(\d+)"
DCINSIDE_URL = r"https://m.dcinside.com/board/{}/{}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36"
}
GALLERY_POSTS_COOKIES = {
    "__gat_mobile_search": "1",
    "list_count": "200",
}


def get_board_post_id(url: str) -> tuple[str, str]:
    res = re.search(DCINSIDE_REGEX, url)
    if not res:
        raise NotDcinsideLink(f"{url} is not a dcinside link.")
    return res[1], res[2]


def get_image_sources_from_dom(soup: BeautifulSoup) -> Iterable[str]:
    for img in soup.find_all("img"):
        if img["src"] == "https://nstatic.dcinside.com/dc/m/img/dccon_loading_nobg200.png":  # loading image as placeholder before loading.
            yield img["data-original"]


async def fetch_post_html(session: ClientSession, board_id: str, post_id: str) -> bytes:
    async with session.get(
        DCINSIDE_URL.format(
            board_id,
            post_id
        ),
        cookies=GALLERY_POSTS_COOKIES,
        headers=HEADERS
    ) as res:
        res.raise_for_status()
        return await res.content.read()


async def save_dcinside_media(url: str, out_dir: PathLike = "./dcinside_media") -> list[str]:
    os.makedirs(out_dir, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        board_id, post_id = get_board_post_id(url)
        board_content = await fetch_post_html(session, board_id, post_id)

        soup = BeautifulSoup(board_content, "lxml")

        paths = []
        for media_url in get_image_sources_from_dom(soup):
            try:
                paths.append(
                    await download_source_url(session, media_url, out_dir=out_dir, filename=f"{board_id}_{post_id}")
                )
            except aiohttp.ClientResponseError:
                logger.exception(f"Error encountered when downloading {media_url}")

        if not paths:
            raise MediaNotFound
        return paths


if __name__ == "__main__":
    import asyncio
    # url = "https://gall.dcinside.com/m/projectmx/7579554"
    url = "https://gall.dcinside.com/mgallery/board/view/?id=projectmx&no=7579554"
    # url = "https://m.dcinside.com/board/projectmx/7579554"

    asyncio.run(save_dcinside_media(url))
