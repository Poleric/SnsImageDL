from _typeshed import SupportsWrite
from pathlib import Path
from typing import Protocol, override, AsyncGenerator, Collection

from snsimagedl_lib import Extractor, FileTagger, Metadata

__all__ = (
    "QueryResult",
    "MediaDownloader"
)


class QueryResult(Protocol):
    extractor: Extractor
    metadata: Metadata

    def save(self, fp: SupportsWrite[bytes]) -> None:
        raise NotImplemented

    def save_to(self, filepath: str | Path) -> None:
        raise NotImplemented


class QueryResultImpl(QueryResult):
    def __init__(self, extractor: Extractor, metadata: Metadata, data: bytes):
        self.extractor = extractor
        self.metadata = metadata
        self.data = data

    @override
    def save(self, fp: SupportsWrite[bytes]) -> None:
        fp.write(self.data)

    @override
    def save_to(self, filepath: str | Path) -> None:
        if not isinstance(filepath, Path):
            filepath = Path(filepath)

        with filepath.open("wb") as f:
            self.save(f)


class MediaDownloader:
    def __init__(self, extractors: Collection[Extractor], taggers: Collection[FileTagger]):
        self.extractors = extractors
        self.taggers = taggers

    async def query(self, query: str) -> AsyncGenerator[QueryResult]:
        for extractor in self.extractors:
            try:
                metadatas = await extractor.query(query)

                for metadata in metadatas:
                    data = await extractor.download(metadata)
                    for tagger in self.taggers:
                        data = tagger.tag(data, metadata)

                    yield QueryResultImpl(extractor, metadata, data)
            except NotImplemented:
                pass
