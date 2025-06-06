from typing import Protocol

from sns_image_dl.metadata import Metadata


class Tagger(Protocol):
    def is_extension_supported(self, extension: str) -> bool:
        raise NotImplementedError

    def tag(self, data: bytes, metadata: Metadata) -> bytes:
        raise NotImplementedError
