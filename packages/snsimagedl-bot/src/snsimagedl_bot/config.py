from dataclasses import dataclass
from pathlib import Path

from snsimagedl_lib import Extractor, FileTagger


@dataclass(slots=True)
class BotConfig:
    extractors: list[Extractor]
    taggers: list[FileTagger]

    output_directory: Path

    watch_channel_ids: set[int]