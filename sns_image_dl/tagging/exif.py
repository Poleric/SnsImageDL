import logging
from typing import override

from pyexiv2 import ImageData

from sns_image_dl.metadata import Metadata
from sns_image_dl.tagging.tagging import Tagger

__all__ = (
    "ExifTagger",
)

logger = logging.getLogger(__name__)

class ExifTagger(Tagger):
    @override
    def is_extension_supported(self, extension: str) -> bool:
        return extension in (".jpg",
                             ".jpeg",
                             ".tiff",
                             ".tif",
                             ".wav",
                             ".png",
                             ".webp")

    @override
    def tag(self, data: bytes, metadata: Metadata) -> bytes:
        with ImageData(data) as img:
            exif = {
                "Exif.Image.DateTime": metadata.get("created_at"),
                "Exif.Image.Artist": metadata.get("artist").get("name"),
                "Exif.Image.XPTitle": metadata.get("title"),
                "Exif.Image.XPComment": metadata.get("description"),
                "Exif.Image.XPAuthor": metadata.get("artist").get("display_name"),
                "Exif.Image.XPKeywords": ";".join(metadata.get("keywords")),
                "Exif.Image.XPSubject": ";".join(metadata.get("keywords")),
                "Exif.Photo.UserComment": metadata.get("description"),
                "Exif.Photo.DateTimeOriginal": metadata.get("created_at")
            }
            img.modify_exif(exif)
            return img.get_bytes()