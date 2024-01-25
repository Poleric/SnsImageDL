import logging
import os
from attrs import define
from pathlib import Path
import filetype
from .tags import Tag, \
    add_xmp, add_exif, add_jpeg_comment

from os import PathLike
type PathLike = str | bytes | PathLike


@define(kw_only=True)
class Media:
    content: bytes
    filename: str
    tags: Tag

    @property
    def extension(self) -> str | None:
        split = self.filename.split(".")
        if len(split) > 1:
            return "." + split[-1].casefold()
        return None

    def guess_extension(self) -> str | None:
        guess = filetype.guess_extension(self)
        if guess:
            return guess.extension
        return None

    def add_metadata(self) -> None:
        extension = self.extension or self.guess_extension()
        data = self.content
        for add_metadata in (add_exif, add_jpeg_comment, add_xmp):
            try:
                data = add_metadata(data, self.tags, extension=extension)
            except ValueError:
                logging.info(f"Tried to {add_metadata.__name__} on {extension}.")
        self.content = data

    def save(self, output_directory: PathLike, *, add_metadata: bool = True):
        if add_metadata:
            self.add_metadata()

        os.makedirs(output_directory, exist_ok=True)
        path = Path(output_directory, self.filename)
        with path.open("wb") as f:
            f.write(self.content)

