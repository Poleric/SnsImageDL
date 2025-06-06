from datetime import datetime
from typing import TypedDict, Sequence


class _Artist(TypedDict):
    handle: str
    display_name: str
    webpage_url: str


class Metadata(TypedDict, total=False):
    title: str
    filename: str
    description: str
    webpage_url: str
    source_url: str
    created_at: datetime
    artist: _Artist
    keywords: Sequence[str]
    type: Sequence[str]
