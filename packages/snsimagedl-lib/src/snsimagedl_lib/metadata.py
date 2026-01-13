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
    filename: str
    source_url: str
    webpage_url: str
    title: str | None = None
    description: str | None = None
    created_at: datetime | None = None
    artist: ArtistMetadata | None = None
    keywords: list[str] | None = None
    type: list[str] | None = None

    @property
    def file_extension(self) -> str:
        """Returns the file extension of the file with the leading `.`"""
        return os.path.splitext(self.filename)[-1]
