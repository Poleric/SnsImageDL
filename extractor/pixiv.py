import asyncio
import os
import re
import functools
from typing import Iterable

from pixivpy3 import AppPixivAPI
from pixivpy3.utils import PixivError
from extractor.base import Extractor, UrlLike, PathLike
from extractor.exceptions import MediaNotFound, InvalidLink

# from typing import override


class NotPixivLink(InvalidLink):
    pass


class Pixiv(Extractor):
    SITE_REGEX = r"https://www.p.?ixiv.net/.*artworks/([0-9]+)"
    API_ARGS = {
        "timeout": 3
    }
    session: AppPixivAPI

    def __init__(self, refresh_token: str = None):
        super().__init__()

        self.loop = asyncio.get_running_loop()
        self.REFRESH_TOKEN = refresh_token or os.getenv("PIXIV_REFRESH_TOKEN")
        assert self.REFRESH_TOKEN, "PIXIV_REFRESH_TOKEN is required. Refer to https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362 to get your refresh token and add it into the environment variable with the name PIXIV_REFRESH_TOKEN"

    # @override
    def __str__(self):
        return "Pixiv"

    # @override
    async def __aenter__(self):
        self.session = await self.loop.run_in_executor(
            None,
            functools.partial(AppPixivAPI, **self.API_ARGS)
        )
        self.session.auth(refresh_token=self.REFRESH_TOKEN)
        return self

    # @override
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return

    # @override
    def get_filename(self, source_url: UrlLike):
        return

    # @override
    async def retrieve_media_urls(self, webpage_url: UrlLike) -> Iterable[str]:
        return self.get_pixiv_media_urls(
            await self.get_pixiv_illust(webpage_url)
        )

    # @override
    async def save(self, webpage_url: UrlLike, output_directory: PathLike) -> None:
        os.makedirs(output_directory, exist_ok=True)

        for media_url in await self.retrieve_media_urls(webpage_url):
            try:
                self.loop.run_in_executor(
                    None,
                    functools.partial(
                        self.session.download,
                        url=media_url,
                        path=output_directory
                    )
                )
            except PixivError:
                self.logger.exception(f"Download {media_url} failed.")

    def get_pixiv_id(self, webpage_url: UrlLike) -> str:
        res = re.search(self.SITE_REGEX, webpage_url)
        if not res:
            raise NotPixivLink
        return res[1]

    async def get_pixiv_illust(self, webpage_url: UrlLike) -> dict:
        # tries 3 times
        illust_id = self.get_pixiv_id(webpage_url)
        for i in range(3):
            try:
                json_result = await self.loop.run_in_executor(
                    None,
                    self.session.illust_detail,
                    illust_id
                )
            except TimeoutError:
                self.logger.warning(f"Timeout when retrieving illustration {illust_id}")
            else:
                if "error" in json_result and "invalid_grant" in json_result["error"]["message"]:
                    self.session.auth()
                    continue
                return json_result.illust

        # if no results
        raise PixivError(f"Error in retrieving {webpage_url} data")

    @staticmethod
    def get_pixiv_media_urls(data: dict) -> list[UrlLike]:
        media_urls = []

        match data:
            case {
                "type": "illust",
                "meta_single_page": page,
                "meta_pages": []
            }:
                media_urls.append(page["original_image_url"])
            case {
                "type": "illust",
                "meta_single_page": {},
                "meta_pages": pages
            }:
                for page in pages:
                    media_urls.append(page["image_urls"]["original"])
            case {
                "type": "ugoira"
            }:
                # TODO: related issues: https://github.com/upbit/pixivpy/issues/164, https://github.com/upbit/pixivpy/issues/253
                raise NotImplemented("Ugoira is a bit iffy to make. will do sometime")
            case _:
                raise MediaNotFound

        return media_urls


if __name__ == "__main__":
    single_illust = "https://www.pixiv.net/en/artworks/97138089"
    multi_illust = "https://www.pixiv.net/en/artworks/115161963"

    async def main():
        async with Pixiv() as pixiv:
            await pixiv.save(multi_illust, "./pixiv_media")

    asyncio.run(main())
