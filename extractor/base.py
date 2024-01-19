import aiohttp
import logging
import filetype
import os
import re
from pathlib import Path
from extractor.exceptions import MediaNotFound, SessionNotCreated

from abc import ABC, abstractmethod
from typing import Iterable

PathLike = str | bytes | os.PathLike
UrlLike = str


class Extractor(ABC):
    SITE_REGEX: str

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    @classmethod
    def check_link(cls, webpage_url: UrlLike) -> bool:
        return bool(re.match(cls.SITE_REGEX, webpage_url))

    @abstractmethod
    def __str__(self):
        raise NotImplemented

    @abstractmethod
    async def save(self, webpage_url: UrlLike, output_directory: PathLike, filename: str = None) -> None:
        """Save all the medias in the specified webpage url.

        :param webpage_url: The webpage to save medias.
        :type webpage_url: str

        :param output_directory: The output directory to save the medias to.
        :type output_directory: PathLike

        :param filename: The filename to save as.
        :type filename: str | None
        """
        raise NotImplemented

    # utils
    @staticmethod
    def save_to(bytes: bytes, output_directory: PathLike, filename: str) -> None:
        path = Path(output_directory, filename)
        with path.open("wb") as f:
            f.write(bytes)

    @staticmethod
    def guess_file_extension(bytes: bytes) -> str | None:
        guess = filetype.guess_extension(bytes)
        if guess:
            return guess.extension

    @staticmethod
    def have_file_extension(filename: str) -> bool:
        return len(filename.split(".")) > 1
