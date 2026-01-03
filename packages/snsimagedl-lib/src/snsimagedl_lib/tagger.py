from typing import Protocol, override
from datetime import datetime

from pyexiv2 import ImageData

from snsimagedl_lib.metadata import Metadata

__all__ = (
    "FileTagger",
    "ExifTagger",
    "XmpTagger",
    "JpegCommentTagger"
)


class FileTagger(Protocol):
    def supports(self, extension: str) -> bool:
        raise NotImplemented

    def tag(self, data: bytes, metadata: Metadata) -> bytes:
        raise NotImplemented


class ExifTagger(FileTagger):
    @override
    def supports(self, extension: str) -> bool:
        return extension in (
            ".jpg",
            ".jpeg",
            ".tiff",
            ".tif",
            ".wav",
            ".png",
            ".webp"
        )

    @override
    def tag(self, data: bytes, metadata: Metadata) -> bytes:
        with ImageData(data) as img:
            exif = {
                "Exif.Image.DateTime": metadata.created_at,
                "Exif.Image.Artist": metadata.artist.handle,
                "Exif.Image.XPTitle": metadata.title,
                "Exif.Image.XPComment": metadata.description,
                "Exif.Image.XPAuthor": metadata.artist.display_name,
                "Exif.Image.XPKeywords": ";".join(metadata.keywords),
                "Exif.Image.XPSubject": ";".join(metadata.keywords),
                "Exif.Photo.UserComment": metadata.description,
                "Exif.Photo.DateTimeOriginal": metadata.created_at
            }
            img.modify_exif(exif)
            return img.get_bytes()


class XmpTagger(FileTagger):
    @override
    def supports(self, extension: str) -> bool:
        return extension in (
            ".jpg",
            ".jpeg",
            ".png",
            # ".gif"
            ".mp3",
            # ".mp4",
            # ".mov",
            # ".pdf",
            ".webp"
        )

    @override
    def tag(self, data: bytes, metadata: Metadata) -> bytes:
        with ImageData(data) as img:
            xmp = {
                "Xmp.xmp.CreateDate": datetime.now(),
                "Xmp.dc.creator": metadata.artist.display_name,
                "Xmp.dc.date": metadata.created_at,
                "Xmp.dc.description": metadata.description,
                "Xmp.dc.source": metadata.webpage_url,
                "Xmp.dc.title": metadata.title,
                "Xmp.dc.subject": metadata.keywords,
                "Xmp.dc.type": metadata.type,
                "Xmp.Iptc4xmpCore.CreatorContactInfo": metadata.artist.webpage_url
            }
            img.modify_xmp(xmp)
            return img.get_bytes()


class JpegCommentTagger(FileTagger):
    @override
    def supports(self, extension: str) -> bool:
        return extension in (
            ".jpg",
            ".jpeg"
        )

    @override
    def tag(self, data: bytes, metadata: Metadata) -> bytes:
        with ImageData(data) as img:
            img.modify_comment(metadata.description)
            return img.get_bytes()
