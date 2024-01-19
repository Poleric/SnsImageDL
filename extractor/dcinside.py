import os
import re
import aiohttp
from bs4 import BeautifulSoup
from extractor.base import Extractor, UrlLike, PathLike
from extractor.exceptions import MediaNotFound, InvalidLink, SessionNotCreated

from typing import Iterable, Mapping


class NotDcinsideLink(InvalidLink):
    pass


class Dcinside(Extractor):
    SITE_REGEX = r"https://(?:gall|m).dcinside.com/[a-zA-Z/]*(?:\?id=|(?:board|m)/)(\w+)(?:&no=|/)(\d+)"
    SCRAPE_ENDPOINT = r"https://m.dcinside.com/board/{}/{}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36"
    }
    # IMAGE_SOURCE_REGEX = r"https://dcimg1.dcinside.com/viewimage.php?id=.+"

    # @override
    def __str__(self):
        return "dcinside"

    # @override
    async def save(self, webpage_url: UrlLike, output_directory: PathLike = "./dcinside_media", filename: str = None):
        if not self.session:
            raise SessionNotCreated("Session is not initialized fully. Use a context manager when saving.")

        webpage_url = self.modify_original_url(webpage_url)
        media_urls = await self.get_media_urls(webpage_url)

        if not media_urls:
            raise MediaNotFound

        os.makedirs(output_directory, exist_ok=True)
        for media_url in media_urls:
            try:
                async with self.session.get(media_url, headers=self.HEADERS) as res:
                    filename = self.get_filename(res.headers)
                    content = await res.content.read()
            except aiohttp.ClientResponseError:
                self.logger.exception(f"Error encountered when downloading {media_url}")
            else:
                self.save_to(content, output_directory, filename)

    async def get_media_urls(self, webpage_url: UrlLike) -> list[UrlLike]:
        soup = BeautifulSoup(await self.fetch_post_html(webpage_url), "lxml")
        return list(self.get_image_sources_from_dom(soup))

    @staticmethod
    def get_image_sources_from_dom(soup: BeautifulSoup) -> Iterable[str]:
        for img in soup.select("img[class='lazy'][data-original]"):
            yield img["data-original"]

    async def fetch_post_html(self, webpage_url: UrlLike) -> bytes:
        async with self.session.get(webpage_url, headers=self.HEADERS) as res:
            res.raise_for_status()
            if not res.ok:
                self.logger.warning(f"Error occurred when fetching {webpage_url}. Error {res.status}")

            return await res.content.read()

    def get_board_and_post_id(self, webpage_url: UrlLike) -> tuple[str, str]:
        res = re.search(self.SITE_REGEX, webpage_url)
        if not res:
            raise NotDcinsideLink(f"{webpage_url} is not a dcinside link.")
        return res[1], res[2]

    def modify_original_url(self, webpage_url: UrlLike) -> UrlLike:
        #  gall.dcinside returns a response that redirects to the m.dcinside endpoint. better off just using m.dcinside
        board_id, post_id = self.get_board_and_post_id(webpage_url)
        return self.SCRAPE_ENDPOINT.format(board_id, post_id)

    @staticmethod
    def get_filename(response_headers: Mapping) -> str:
        # 'Content-Disposition': 'attachment; filename=1705115980.png'
        return response_headers["Content-Disposition"].rsplit('=')[-1]


if __name__ == "__main__":
    import asyncio
    # url = "https://gall.dcinside.com/m/projectmx/7579554"
    url = "https://gall.dcinside.com/mgallery/board/view/?id=projectmx&no=7579554"
    # url = "https://m.dcinside.com/board/projectmx/7579554"

    async def main():
        async with Dcinside() as dcinside:
            await dcinside.save(url)

    asyncio.run(main())

