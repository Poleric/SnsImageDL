from dataclasses import dataclass
from pathlib import Path
from typing import Collection

from snsimagedl_lib import Extractor, FileTagger, MediaDownloader

__all__ = (
    "BotConfig",
)


@dataclass(slots=True)
class BotConfig:
    extractors: Collection[Extractor]
    taggers: Collection[FileTagger]

    output_directory: Path

    watch_channel_ids: set[int]

    @property
    def downloader(self) -> MediaDownloader:
        return MediaDownloader(self.extractors, self.taggers)
