from .extractor import *
from .metadata import *
from .tagger import *
from .downloader import *


DEFAULT_TAGGERS: list[type[FileTagger]] = [
    ExifTagger,
    XmpTagger,
    JpegCommentTagger
]