from dataclasses import dataclass
from datetime import datetime
import os


__all__ = (
    "ArtistMetadata",
    "Metadata"
)

@dataclass(slots=True, frozen=True)
class ArtistMetadata:
    handle: str
    display_name: str
    webpage_url: str


@dataclass(slots=True, frozen=True)
class Metadata:
    title: str
    filename: str
    description: str
    webpage_url: str
    source_url: str
    created_at: datetime
    artist: ArtistMetadata
    keywords: list[str]
    type: list[str]

    @property
    def file_extension(self) -> str:
        """Returns the file extension of the file with the leading `.`"""
        return os.path.splitext(self.filename)[-1]
