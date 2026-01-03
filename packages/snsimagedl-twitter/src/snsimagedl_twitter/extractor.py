from typing import override

import aiohttp

from snsimagedl_lib import Extractor, Metadata


class TwitterExtractor(Extractor):
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    @override
    async def query(self, query: str) -> tuple[Metadata] | None:
        ...

    @override
    async def download(self, media: Metadata) -> bytes:
        ...