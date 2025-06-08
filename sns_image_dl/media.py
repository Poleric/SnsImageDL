from typing import NamedTuple

from sns_image_dl.metadata import Metadata


class Media(NamedTuple):
    content: bytes
    metadata: Metadata

    def __repr__(self):
        return "Media(" \
               f"content={self.content[:16] + b"..." if len(self.content) > 16 else self.content}, " \
               f"metadata={self.metadata}" \
               ")"
