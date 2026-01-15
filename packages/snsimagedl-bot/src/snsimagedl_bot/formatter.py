from dataclasses import dataclass, asdict
from pathlib import Path
from string import Formatter
from typing import override, Self

from snsimagedl_lib import QueryResult


@dataclass(slots=True, frozen=True)
class FilePathContext:
    extractor: str
    filename: str
    ext: str

    @classmethod
    def from_query(cls, result: QueryResult) -> Self:
        return cls(
            extractor=result.extractor.__class__.__name__.removesuffix("Extractor").lower(),
            filename=Path(result.metadata.filename).stem,
            ext=result.metadata.file_extension.removeprefix(".")
        )


class FilePathFormatter(Formatter):
    def compile_path(self, fmt: str, *, context: FilePathContext) -> Path:
        return Path(self.format(fmt, **asdict(context)))
