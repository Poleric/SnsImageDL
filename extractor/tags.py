from pyexiv2 import ImageData
from datetime import datetime
from filetype import guess_extension
from typing import Sequence, TypedDict, Final


type UrlLike = str
type AsciiStr = str


class TagArtist(TypedDict, total=False):
    name: AsciiStr
    display_name: str
    webpage_url: UrlLike


class Tag(TypedDict, total=False):
    title: str
    description: str
    webpage_url: UrlLike
    source_url: UrlLike
    created_at: str
    artist: TagArtist
    keywords: Sequence[str]
    type: Sequence[str]


def _check_extension_supported(data: bytes, allowed_extensions: Sequence[str], extension: str = None):
    if extension is None:
        guess = guess_extension(data)
        if not guess:
            raise ValueError(f"{extension} file does not have a valid extension")
        extension = guess.extension

    return extension in allowed_extensions


XMP_SUPPORTED_EXTENSIONS: Final[tuple[str, ...]] = (
    ".jpg",
    ".jpeg",
    ".png",
    ".gif"
    ".mp3",
    ".mp4",
    ".mov",
    ".pdf",
    ".webp"
)

JPEG_COM_SUPPORTED_EXTENSIONS: Final[tuple[str, ...]] = (
    ".jpg",
    ".jpeg"
)

EXIF_SUPPORTED_EXTENSIONS: Final[tuple[str, ...]] = (
    ".jpg",
    ".jpeg",
    ".tiff",
    ".tif",
    ".wav",
    ".png",
    ".webp"
)


def add_exif(data: bytes, tag: Tag, *, extension: str = None) -> bytes:
    if not _check_extension_supported(data, EXIF_SUPPORTED_EXTENSIONS, extension):
        raise ValueError(f"{extension} is not supported for Exif.")

    with ImageData(data) as img:
        exif = {
            "Exif.Image.DateTime": tag.get("created_at"),
            "Exif.Image.Artist": tag.get("artist").get("name"),
            "Exif.Image.XPTitle": tag.get("title"),
            "Exif.Image.XPComment": tag.get("description"),
            "Exif.Image.XPAuthor": tag.get("artist").get("display_name"),
            "Exif.Image.XPKeywords": ";".join(tag.get("keywords")),
            "Exif.Photo.UserComment": tag.get("description"),
            "Exif.Photo.DateTimeOriginal": tag.get("created_at")
        }
        img.modify_exif(exif)
        return img.get_bytes()


def add_jpeg_comment(data: bytes, tag: Tag, *, extension: str = None) -> bytes:
    if not _check_extension_supported(data, JPEG_COM_SUPPORTED_EXTENSIONS, extension):
        raise ValueError(f"{extension} is not supported for JPEG comments.")

    with ImageData(data) as img:
        img.modify_comment(tag.get("description"))
        return img.get_bytes()


def add_xmp(data: bytes, tag: Tag, *, extension: str = None) -> bytes:
    if not _check_extension_supported(data, XMP_SUPPORTED_EXTENSIONS, extension):
        raise ValueError(f"{extension} is not supported for XMP.")

    with ImageData(data) as img:
        xmp = {
            "Xmp.xmp.CreateDate": datetime.now(),
            "Xmp.dc.creator": tag.get("artist").get("display_name"),
            "Xmp.dc.date": tag.get("created_at"),
            "Xmp.dc.description": tag.get("description"),
            "Xmp.dc.source": tag.get("webpage_url"),
            "Xmp.dc.title": tag.get("title"),
            "Xmp.dc.subject": tag.get("keywords"),
            "Xmp.dc.type": tag.get("type"),
            "Xmp.Iptc4xmpCore.CreatorContactInfo": tag.get("artist").get("webpage_url")
        }
        img.modify_xmp(xmp)
        return img.get_bytes()
