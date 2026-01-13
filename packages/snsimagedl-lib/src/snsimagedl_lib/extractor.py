from typing import Protocol, Collection

from snsimagedl_lib.metadata import Metadata

__all__ = (
    "Extractor",
)


class Extractor[T: Metadata](Protocol):
    async def query(self, query: str) -> Collection[T] | None:
        raise NotImplemented

    async def download(self, media: T) -> bytes:
        raise NotImplemented
