import asyncio
import functools
import logging
import re
from io import BytesIO
from typing import override, Iterable, Collection

import msgspec
from pixivpy3 import AppPixivAPI, PixivError
from yarl import URL

from snsimagedl_lib import Extractor, Metadata, ArtistMetadata
from snsimagedl_lib.exceptions import UnsupportedLink
from snsimagedl_pixiv.models import IllustDetails, MetaSinglePage

__all__ = (
    "PixivExtractor",
)

logger = logging.getLogger(__name__)


class PixivExtractor(Extractor):
    URL_PATTERN: re.Pattern = re.compile(r"https://.*p.?ixiv.net/.*artworks/([0-9]+)")

    def __init__(self, refresh_token: str):
        self.refresh_token = refresh_token
        self.loop = asyncio.get_running_loop()

        self.session = AppPixivAPI(timeout=3)
        self.session.auth(refresh_token=refresh_token)

    def _get_illust_id(self, url: str) -> str:
        res = self.URL_PATTERN.search(url)
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
            case IllustDetails(type="illust", meta_single_page=MetaSinglePage(original_image_url=None),
                               meta_pages=pages):
                for page in pages:
                    yield page.image_urls.original
            case IllustDetails(type="ugoira"):
                # TODO: related issues: https://github.com/upbit/pixivpy/issues/164, https://github.com/upbit/pixivpy/issues/253
                raise NotImplementedError("Ugoira is a bit iffy to make. will do sometime")
            case _:
                logger.error(f"Unexpected type. Raw dump: {msgspec.json.encode(illust)}")
                raise NotImplementedError

    @override
    async def query(self, query: str) -> Collection[Metadata] | None:
        illust_id = self._get_illust_id(query)

        illust = await self._fetch(illust_id)
        results = []
        for source_url in self._get_source_urls(illust):
            results.append(Metadata(
                filename=URL(source_url).name,
                source_url=source_url,
                webpage_url=query,
                title=illust.title,
                description=illust.caption.replace("<br />", "\n"),
                created_at=illust.create_date,
                artist=ArtistMetadata(
                    handle=illust.user.account,
                    display_name=illust.user.name,
                    webpage_url=f"https://www.pixiv.net/users/{illust.user.id}"
                ),
                keywords=[tag.name for tag in illust.tags]
            ))
        return results

    @override
    async def download(self, media: Metadata) -> bytes:
        with BytesIO() as f:
            try:
                await self.loop.run_in_executor(
                    None,
                    functools.partial(
                        self.session.download,
                        url=media.source_url,
                        fname=f
                    )
                )  # noqa
                return f.getvalue()
            except PixivError:
                logger.exception(f"Download for {media.source_url} failed.")
                raise
