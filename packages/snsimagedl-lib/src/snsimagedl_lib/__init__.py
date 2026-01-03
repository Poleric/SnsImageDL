from .extractor import *
from .metadata import *
from .tagger import *

DEFAULT_TAGGERS: list[type[FileTagger]] = [
    ExifTagger,
    XmpTagger,
    JpegCommentTagger
]