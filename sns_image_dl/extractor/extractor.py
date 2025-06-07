from typing import Protocol, AsyncGenerator

from sns_image_dl.media import Media


class Extractor(Protocol):
    def is_link_supported(self, url: str) -> bool:
        raise NotImplementedError

    def extract(self, url: str) -> AsyncGenerator[Media, None]:
        raise NotImplementedError
