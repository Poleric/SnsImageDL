from typing import Collection

import aiohttp
from msgspec import Struct

from snsimagedl_lib import Extractor, FileTagger, ExifTagger, XmpTagger, JpegCommentTagger, MediaDownloader
from snsimagedl_pixiv import PixivExtractor
from snsimagedl_twitter import TwitterExtractor

__all__ = (
    "session",
    "AppConfig",
)


session: aiohttp.ClientSession | None = None


def config_namer(name: str) -> str:
    name = name.lower()
    return name.removesuffix("config")


class ExtractorConfig[T: Extractor](Struct, tag_field="type", tag=config_namer):
    type: str
    output_directory: str | None = None

    @property
    def instance(self) -> T:
        raise NotImplementedError


class TwitterConfig(ExtractorConfig[TwitterExtractor], kw_only=True):
    token: str | None = None

    @property
    def instance(self) -> TwitterExtractor:
        return TwitterExtractor(session)


class PixivConfig(ExtractorConfig[PixivExtractor], kw_only=True):
    refresh_token: str

    @property
    def instance(self) -> PixivExtractor:
        return PixivExtractor(self.refresh_token)


class TaggerConfig[T: FileTagger](Struct, tag_field="type", tag=config_namer):
    type: str

    @property
    def instance(self) -> T:
        raise NotImplementedError


class ExifConfig(TaggerConfig[ExifTagger], kw_only=True):
    @property
    def instance(self) -> ExifTagger:
        return ExifTagger()


class XmpConfig(TaggerConfig[XmpTagger], kw_only=True):
    @property
    def instance(self) -> XmpTagger:
        return XmpTagger()


class JpegConfig(TaggerConfig[JpegCommentTagger], kw_only=True):
    @property
    def instance(self) -> JpegCommentTagger:
        return JpegCommentTagger()


class BotConfig(Struct, kw_only=True):
    token: str
    command_prefix: str


class AppConfig(Struct, kw_only=True):
    bot: BotConfig
    watch_channel_ids: set[int]
    output_directory: str
    extractors: Collection[TwitterConfig | PixivConfig] = []
    taggers: Collection[ExifConfig | XmpConfig | JpegConfig] = []

    @property
    def downloader(self) -> MediaDownloader:
        return MediaDownloader(
            [config.instance for config in self.extractors],
            [config.instance for config in self.taggers]
        )

