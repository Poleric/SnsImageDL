import logging
from typing import override

from pyexiv2 import ImageData

from sns_image_dl.metadata import Metadata
from sns_image_dl.tagging.tagging import Tagger

__all__ = (
    "JpegCommentTagger",
)

logger = logging.getLogger(__name__)

class JpegCommentTagger(Tagger):
    @override
    def is_extension_supported(self, extension: str) -> bool:
        return extension in (".jpg",
                             ".jpeg")

    @override
    def tag(self, data: bytes, metadata: Metadata) -> bytes:
        with ImageData(data) as img:
            img.modify_comment(metadata.get("description"))
            return img.get_bytes()
