import asyncio
import os
import re
import functools
import logging
from io import BytesIO
import json
from pixivpy3 import AppPixivAPI
from pixivpy3.utils import PixivError
from ..extractor import Extractor, UrlLike
from ..exceptions import MediaNotFound, InvalidLink
from ..media import Media
from ..tags import Tag

from typing import override, Iterable
from .response_typing import IllustDetails


class NotPixivLink(InvalidLink):
    pass


def get_pixiv_media_urls(illust_details: IllustDetails) -> Iterable[UrlLike]:
    match illust_details:
        case {
            "type": "illust",
            "meta_single_page": page,
            "meta_pages": []
        }:
            yield page["original_image_url"]
        case {
            "type": "illust",
            "meta_single_page": {},
            "meta_pages": pages
        }:
            for page in pages:
                yield page["image_urls"]["original"]
        case {
            "type": "ugoira"
        }:
            # TODO: related issues: https://github.com/upbit/pixivpy/issues/164, https://github.com/upbit/pixivpy/issues/253
            raise NotImplemented("Ugoira is a bit iffy to make. will do sometime")
        case {
            "type": unknown
        }:
            logging.debug(
                f"Unexpected type {unknown}. \n"
                f"Full dump: {json.dumps(illust_details, indent=4)}"
            )
            raise MediaNotFound


class Pixiv(Extractor):
    URL_REGEX = r"https://www.p.?ixiv.net/.*artworks/([0-9]+)"
    API_ARGS = {
        "timeout": 3
    }
    session: AppPixivAPI

    def __init__(self, refresh_token: str = None):
        super().__init__()

        self.loop = asyncio.get_running_loop()
        self.REFRESH_TOKEN = refresh_token or os.getenv("PIXIV_REFRESH_TOKEN")
        assert self.REFRESH_TOKEN, "PIXIV_REFRESH_TOKEN is required. Refer to https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362 to get your refresh token and add it into the environment variable with the name PIXIV_REFRESH_TOKEN"

    @override
    async def __aenter__(self):
        self.session = await self.loop.run_in_executor(
            None,
            functools.partial(AppPixivAPI, **self.API_ARGS)
        )
        self.session.auth(refresh_token=self.REFRESH_TOKEN)
        return self

    @override
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return

    @override
    async def get_all_media(self, webpage_url: UrlLike) -> Iterable[Media]:
        illust_details = await self.fetch_illust(webpage_url)

        for source_url in get_pixiv_media_urls(illust_details):
            tag: Tag = {
                "title": illust_details["title"],
                "description": illust_details["caption"].replace("<br />", "\n"),
                "webpage_url": webpage_url,
                "source_url": source_url,
                "created_at": illust_details["create_date"],
                "artist": {
                    "name": illust_details["user"]["account"],
                    "display_name": illust_details["user"]["name"],
                    "webpage_url": f"https://www.pixiv.net/users/{illust_details["user"]["id"]}"
                },
                "keywords": [pixiv_tag["name"] for pixiv_tag in illust_details["tags"]]
            }
            with BytesIO() as content:
                try:
                    await self.loop.run_in_executor(
                        None,
                        functools.partial(
                            self.session.download,
                            url=source_url,
                            fname=content
                        )
                    )
                except PixivError:
                    logging.exception(f"Download {source_url} failed.")

                media = Media(
                    content=content.getvalue(),
                    filename=self.get_url_basename(source_url),
                    tags=tag
                )
                yield media

    def get_pixiv_id(self, webpage_url: UrlLike) -> str:
        res = re.search(self.URL_REGEX, webpage_url)
        if not res:
            raise NotPixivLink
        return res[1]

    async def fetch_illust(self, webpage_url: UrlLike) -> IllustDetails:
        illust_id = self.get_pixiv_id(webpage_url)

        for i in range(3):
            try:
                json_result = await self.loop.run_in_executor(
                    None,
                    self.session.illust_detail,
                    illust_id
                )
            except TimeoutError:
                logging.warning(f"Timeout when retrieving illustration {illust_id}")
            else:
                if "error" in json_result and "invalid_grant" in json_result["error"]["message"]:
                    self.session.auth()
                    continue
                return json_result.illust

        # if no results
        raise PixivError(f"Error in retrieving {webpage_url} data")


if __name__ == "__main__":
    single_illust = "https://www.pixiv.net/en/artworks/97138089"
    multi_illust = "https://www.pixiv.net/en/artworks/115161963"
    description_illust = "https://www.pixiv.net/en/artworks/114913218"
    ugoira = "https://www.pixiv.net/en/artworks/115451299"

    async def main():
        async with Pixiv() as pixiv:
            os.makedirs("./pixiv_media", exist_ok=True)
            async for media in pixiv.get_all_media(multi_illust):
                media.save(output_directory="./pixiv_media", add_metadata=True)


    asyncio.run(main())
