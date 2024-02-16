import aiohttp
import os
import re
from .media import Media

from abc import ABC, abstractmethod
from typing import Iterable

type PathLike = str | bytes | os.PathLike
type UrlLike = str


class Extractor(ABC):
    URL_REGEX: str

    def __init__(self):
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def __str__(self):
        return self.__class__.__name__

    @classmethod
    def check_link(cls, webpage_url: UrlLike) -> bool:
        return bool(re.match(cls.URL_REGEX, webpage_url))

    @staticmethod
    def get_url_basename(source_url: UrlLike) -> str:
        return os.path.basename(source_url).split("?")[0]

    @abstractmethod
    async def get_all_media(self, webpage_url: UrlLike) -> Iterable[Media]:
        """
        :param webpage_url: The webpage to fetch its media from.
        :type webpage_url: UrlLike

        :return:
        :rtype: Iterable[Media]
        """
        raise NotImplementedError

