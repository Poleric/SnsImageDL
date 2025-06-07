import logging
import re
from typing import override, AsyncGenerator

from sns_image_dl.exceptions import UnsupportedLink
from sns_image_dl.extractor.extractor import Extractor

__all__ = (
    "Dcinside",
)

from sns_image_dl.media import Media

logger = logging.getLogger(__name__)


class Dcinside(Extractor):
    URL_REGEX: re.Pattern = re.compile(
        r"https://(?:gall|m).dcinside.com/[a-zA-Z/]*(?:\?id=|(?:board|m)/)(\w+)(?:&no=|/)(\d+)")

    def __init__(self):
        raise NotImplementedError

    @override
    def is_link_supported(self, url: str) -> bool:
        return bool(self.URL_REGEX.match(url))

    def _get_ids(self, url: str) -> tuple[str, str]:
        """Extract the board id and post id from the url"""
        res = re.search(self.URL_REGEX, url)
        if not res:
            raise UnsupportedLink(f"{url} is not a dcinside link.")
        return res[1], res[2]

    @override
    async def extract(self, url: str) -> AsyncGenerator[Media, None]:  # noqa
        raise NotImplementedError
        # TODO: im lazy
