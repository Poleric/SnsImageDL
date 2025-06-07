import asyncio
import functools
import logging
import re
from io import BytesIO
from typing import override, Iterable, AsyncGenerator

import msgspec
from pixivpy3 import AppPixivAPI, PixivError
from yarl import URL

from sns_image_dl.exceptions import UnsupportedLink
from sns_image_dl.extractor.extractor import Extractor
from sns_image_dl.extractor.pixiv.models import *
from sns_image_dl.media import Media
from sns_image_dl.metadata import Metadata

__all__ = (
    "Pixiv",
)

logger = logging.getLogger(__name__)


class Pixiv(Extractor):
    URL_REGEX: re.Pattern = re.compile(r"https://.*p.?ixiv.net/.*artworks/([0-9]+)")

    def __init__(self, refresh_token: str):
        self.refresh_token = refresh_token
        self.loop = asyncio.get_running_loop()

        self.session = AppPixivAPI(timeout=3)
        self.session.auth(refresh_token=refresh_token)

    @override
    def is_link_supported(self, url: str) -> bool:
        return bool(self.URL_REGEX.match(url))

    def _get_illust_id(self, url: str) -> str:
        res = self.URL_REGEX.search(url)
        if not res:
            raise UnsupportedLink(f"{url} is not a Pixiv link.")
        return res[1]

    async def _fetch(self, illust_id: str) -> IllustDetails:
        for i in range(3):
            try:
                json_result = await self.loop.run_in_executor(
                    None,
                    self.session.illust_detail,
                    illust_id, True
                )
            except TimeoutError:
                logger.exception(f"Timeout when retrieving illustration {illust_id}")
            else:
                if "error" in json_result and "invalid_grant" in json_result["error"]["message"]:
                    self.session.auth()
                    continue
                return msgspec.convert(json_result["illust"], type=IllustDetails, strict=False)
        raise PixivError(f"Error in retrieving illustration {illust_id}")

    @staticmethod
    def _get_source_urls(illust: IllustDetails) -> Iterable[str]:
        match illust:  # noqa
            case IllustDetails(type="illust", meta_single_page=page, meta_pages=[]):
                yield page.original_image_url
            case IllustDetails(type="illust", meta_single_page=MetaSinglePage(original_image_url=None), meta_pages=pages):
                for page in pages:
                    yield page.image_urls.original
            case IllustDetails(type="ugoira"):
                # TODO: related issues: https://github.com/upbit/pixivpy/issues/164, https://github.com/upbit/pixivpy/issues/253
                raise NotImplementedError("Ugoira is a bit iffy to make. will do sometime")
            case _:
                logger.error(f"Unexpected type. Raw dump: {msgspec.json.encode(illust)}")
                raise NotImplementedError

    @override
    async def extract(self, url: str) -> AsyncGenerator[Media, None]:
        illust_id = self._get_illust_id(url)

        illust = await self._fetch(illust_id)
        for source_url in self._get_source_urls(illust):
            metadata: Metadata = {
                "filename": URL(source_url).name,
                "title": illust.title,
                "description": illust.caption.replace("<br />", "\n"),
                "webpage_url": url,
                "source_url": source_url,
                "created_at": illust.create_date,
                "artist": {
                    "handle": illust.user.account,
                    "display_name": illust.user.name,
                    "webpage_url": f"https://www.pixiv.net/users/{illust.user.id}"
                },
                "keywords": [tag.name for tag in illust.tags]
            }

            with BytesIO() as f:
                try:
                    await self.loop.run_in_executor(
                        None,
                        functools.partial(
                            self.session.download,
                            url=source_url,
                            fname=f
                        )
                    )  # noqa
                except PixivError:
                    logger.exception(f"Download for {source_url} failed.")
                    raise

                yield Media(f.getvalue(), metadata)
