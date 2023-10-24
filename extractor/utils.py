import aiohttp
import logging
import filetype

logger = logging.getLogger(__name__)


class MISSING:
    def __bool__(self):
        return False


def build_filepath(
        out_dir: str,
        filename: str,
        file_ext: str | None = MISSING,
        *,
        bytes_to_guess: bytes = None) -> str:
    """
    :param out_dir: The output directory
    :param filename: The filename
    :param file_ext: The file extension. The period sign ``.`` is not required when passed in.
        When :class:`None` is passed, no file extension is appended to the end of the file.
        ``bytes_to_guess`` is `required` if not specified
    :param bytes_to_guess: The :class:`bytes` to guess the extension when ``file_ext`` is not specified.
        `Required` if ``file_ext`` is not specified

    :return: The fully built filepath
    """
    path = f"{out_dir}/"

    path += filename

    if file_ext is not None:
        # tries to guess extension if unspecified
        if file_ext is MISSING:
            if not bytes_to_guess:
                raise ValueError("File extension is not specified. Did you mean to put `None`?")

            guess = filetype.guess(bytes_to_guess)  # can be None
            if guess is not None:
                file_ext = guess.extension
            else:
                logger.warning(f"File extension not found for {filename=}")

        if file_ext:  # add only IF file extension exists. (guessing might return None)
            path += f".{file_ext.strip('.')}"

    return path


async def download_source_url(
        session: aiohttp.ClientSession,
        url: str,
        *,
        out_dir: str,
        filename: str,
        file_ext: str | None = MISSING) -> str:
    """
    :param session: The aiohttp ClientSession.
    :param url: The source url to the media to be downloaded.

    :param out_dir: The output directory
    :param filename: The filename
    :param file_ext: The file extension of the file.
        Specify :class:`None` for no file extension.

    :return: The relative filepath of the saved media
    """

    async with session.get(url) as res:
        res.raise_for_status()
        content = await res.content.read()

        path = build_filepath(out_dir, filename, file_ext, bytes_to_guess=content)

        with open(path, 'wb') as handle:
            if not res.ok:
                logger.warning(res)
            handle.write(content)

    return path
