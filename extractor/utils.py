import requests
import logging
import filetype
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
MISSING = object()


def download_source_url(
        url: str, *,
        out_dir: str,
        file_name: str,
        file_ext: str | type[MISSING] | None = MISSING
    ) -> None:
    """
    :param url: The source url to the media to be downloaded.
    :param out_dir: The output directory of the file.
    :param file_name: The file name of the file.
    :param file_ext: The file extension of the file. If unspecified, the filetype would be guessed instead. Pass in None to not have any extension.
    """

    response = requests.get(url)

    path = f"{out_dir}/"
    path += file_name

    if file_ext is not None:
        if file_ext is MISSING:
            file_ext = filetype.guess(response.content).extension

        if file_ext:
            path += f".{file_ext}"

    with open(path, 'wb') as handle:
        if not response.ok:
            logger.warning(response)
        handle.write(response.content)
