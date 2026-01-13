from dataclasses import dataclass
from pathlib import Path
from typing import Collection, TYPE_CHECKING

from snsimagedl_lib import Extractor, FileTagger, Metadata

if TYPE_CHECKING:
    from _typeshed import SupportsWrite

__all__ = (
    "QueryResult",
    "DownloadResult",
    "MediaDownloader",
)


@dataclass(slots=True, frozen=True)
class QueryResult:
    extractor: Extractor
    metadata: Metadata

    downloader: MediaDownloader

    async def _download_data(self) -> bytes:
        return await self.extractor.download(self.metadata)

    async def download(self) -> DownloadResult:
        return DownloadResult(
            await self._download_data(),
            self
        )


@dataclass(slots=True, frozen=True)
class DownloadResult:
    data: bytes

    query: QueryResult

    def tag(self, taggers: Collection[FileTagger] = None) -> DownloadResult:
        data = self.data
        taggers = taggers or self.query.downloader.taggers

        for tagger in taggers:
            data = tagger.tag(data, self.query.metadata)
        return DownloadResult(data, self.query)

    def save(self, fp: SupportsWrite[bytes]) -> None:
        fp.write(self.data)

    def save_to(self, filepath: str | Path) -> None:
        if not isinstance(filepath, Path):
            filepath = Path(filepath)

        with filepath.open("wb") as f:
            # noinspection PyTypeChecker
            self.save(f)


class MediaDownloader:
    def __init__(self, extractors: Collection[Extractor], taggers: Collection[FileTagger]):
        self.extractors = extractors
        self.taggers = taggers

    async def query(self, query: str) -> Collection[QueryResult]:
        results = []

        for extractor in self.extractors:
            try:
                for metadata in await extractor.query(query):
                    results.append(QueryResult(extractor, metadata, self))
            except NotImplemented:
                pass

        return results
