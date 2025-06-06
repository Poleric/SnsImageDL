import logging
from datetime import datetime
from typing import override

from pyexiv2 import ImageData

from sns_image_dl.metadata import Metadata
from sns_image_dl.tagging.tagging import Tagger

__all__ = (
    "XmpTagger",
)

logger = logging.getLogger(__name__)

class XmpTagger(Tagger):
    @override
    def is_extension_supported(self, extension: str) -> bool:
        return extension in (".jpg",
                             ".jpeg",
                             ".png",
                             # ".gif"
                             ".mp3",
                             # ".mp4",
                             # ".mov",
                             # ".pdf",
                             ".webp")

    @override
    def tag(self, data: bytes, metadata: Metadata) -> bytes:
        with ImageData(data) as img:
            xmp = {
                "Xmp.xmp.CreateDate": datetime.now(),
                "Xmp.dc.creator": metadata.get("artist").get("display_name"),
                "Xmp.dc.date": metadata.get("created_at"),
                "Xmp.dc.description": metadata.get("description"),
                "Xmp.dc.source": metadata.get("webpage_url"),
                "Xmp.dc.title": metadata.get("title"),
                "Xmp.dc.subject": metadata.get("keywords"),
                "Xmp.dc.type": metadata.get("type"),
                "Xmp.Iptc4xmpCore.CreatorContactInfo": metadata.get("artist").get("webpage_url")
            }
            img.modify_xmp(xmp)
            return img.get_bytes()
