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

    @abstractmethod
    def __str__(self):
        raise NotImplemented

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    @abstractmethod
    def get_filename(self, source_url: UrlLike):
        raise NotImplemented

    @abstractmethod
    async def retrieve_media_urls(self, webpage_url: UrlLike) -> Iterable[str]:
        raise NotImplemented

    @classmethod
    def check_link(cls, webpage_url: UrlLike) -> bool:
        return bool(re.match(cls.SITE_REGEX, webpage_url))

    async def save(self, webpage_url: UrlLike, output_directory: PathLike) -> tuple[list[PathLike], list[UrlLike]]:
        """Save all the medias in the specified webpage url.

        :param webpage_url: The webpage to save medias.
        :type webpage_url: str

        :param output_directory: The output directory to save the medias to.
        :type output_directory: PathLike

        :returns: A len 2 tuple, first containing the successful downloads as a relative path, second containing failed downloads as the media source url.
        :rtype: Tuple[List[PathLike], List[str]]

        :raises MediaNotFound: If no media are successfully downloaded.
        :raises SessionNotCreated: If the class is not initialized fully. Use a context manager.
        """
        if not self.session:
            raise SessionNotCreated("Session is not initialized fully. Use a context manager when saving.")

        os.makedirs(output_directory, exist_ok=True)

        downloaded = []
        failed = []
        for media_url in await self.retrieve_media_urls(webpage_url):
            try:
                path = await self.download_media(
                    media_url,
                    output_directory=output_directory,
                    filename=self.get_filename(media_url)
                )
                downloaded.append(path)
            except aiohttp.ClientResponseError:
                self.logger.exception(f"Error encountered when downloading {media_url}")
                failed.append(media_url)

        if not downloaded:
            raise MediaNotFound
        return downloaded, failed

    async def download_media_bytes(self, session: aiohttp.ClientSession, source_url: UrlLike) -> bytes:
        """Download the media in the specified url and return as bytes."""
        async with session.get(source_url) as res:
            res.raise_for_status()

            if not res.ok:
                self.logger.warning(res)

            return await res.content.read()

    async def download_media(
            self,
            source_url: UrlLike,
            *,
            output_directory: PathLike,
            filename: str,

            default_extension: str = "jpg"
        ) -> PathLike:
        """
        :param source_url: The source url to the media to be downloaded.
        :type source_url: str

        :param output_directory: The output directory
        :type output_directory: PathLike

        :param filename: The filename
        :type filename: str

        :param default_extension: The defaulted extension when no file extension is found and can't be guessed.
        :type default_extension: str

        :return: The relative filepath of the saved media
        :rtype: PathLike
        """

        content = await self.download_media_bytes(self.session, source_url)

        filepath = Path(output_directory, filename)

        # no file extension
        if not filepath.suffix:
            guess = filetype.guess(content)  # can be None
            if guess is None:
                self.logger.warning(f"File extension not found for file \"{filename}\". Defaulting to {default_extension}")

            filepath = filepath.with_suffix(guess.extension if guess else default_extension)

        with filepath.open('wb') as handle:
            handle.write(content)

        return str(filepath)

