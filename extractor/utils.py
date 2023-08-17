import requests
import logging

logger = logging.getLogger(__name__)


def download_source_url(url: str, path: str):
    with open(f"{path}", 'wb') as handle:
        response = requests.get(url, stream=True)

        if not response.ok:
            logger.warning(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)
