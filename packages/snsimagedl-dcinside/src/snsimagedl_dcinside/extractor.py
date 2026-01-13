from typing import override, Collection

import aiohttp

from snsimagedl_lib import Extractor, Metadata


class DcinsideExtractor(Extractor):
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    @override
    async def query(self, query: str) -> Collection[Metadata] | None:
        ...

    @override
    async def download(self, media: Metadata) -> bytes:
        ...