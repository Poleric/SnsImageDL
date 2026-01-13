import re
from typing import override, Collection, ClassVar

import aiohttp

from snsimagedl_lib import Extractor, Metadata


class DcinsideExtractor(Extractor):
    URL_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"https://(?:gall|m).dcinside.com/[a-zA-Z/]*(?:\?id=|(?:board|m)/)(\w+)(?:&no=|/)(\d+)"
    )

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    @override
    async def query(self, query: str) -> Collection[Metadata] | None:
        ...

    @override
    async def download(self, media: Metadata) -> bytes:
        ...