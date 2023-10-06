import requests
import logging
import filetype

logger = logging.getLogger(__name__)


def download_source_url(url: str, *, out_dir: str, file_name: str, file_ext: str = None) -> None:
    """
    :param url: The source url to the media to be downloaded.
    :param out_dir: The output directory of the file.
    :param file_name: The file name of the file.
    :param file_ext: The file extension of the file. Can be left none, where the filetype will be based on the binaries.
                Leave empty string to specify no file extension, or file extension is already in the file_name
    """

    response = requests.get(url)

    path = ""
    path += f"{out_dir}/"

    if not file_name:  # cannot be empty
        file_name = ...
    path += file_name

    if file_ext is None:
        file_ext = filetype.guess(response.content).extension
    if file_ext:
        path += f".{file_ext}"

    with open(path, 'wb') as handle:

        if not response.ok:
            logger.warning(response)

        handle.write(response.content)
