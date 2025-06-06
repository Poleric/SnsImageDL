from typing import NamedTuple

from sns_image_dl.metadata import Metadata


class Media(NamedTuple):
    content: bytes
    metadata: Metadata
