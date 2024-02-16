import re
import logging
import aiohttp
from bs4 import BeautifulSoup
from ..base import Extractor, UrlLike
from ..exceptions import InvalidLink
from ..tags import Tag
from ..media import Media

from typing import Iterable, override



class NotDcinsideLink(InvalidLink):
    pass


def modify_webpage_url(board_id: str, post_id: str) -> UrlLike:
    return "https://gall.dcinside.com/mgallery/board/view/?id={}&no={}".format(board_id, post_id)


def get_image_sources_from_dom(soup: BeautifulSoup) -> Iterable[str]:
    for a in soup.select(".appending_file a"):
        yield a["href"]


def get_title_from_dom(soup: BeautifulSoup) -> str:
    return soup.find("span", class_="title_subject").get_text(strip=True)


def get_datetime_from_dom(soup: BeautifulSoup) -> str:
    """
    :return: datetime string in format of "YYYY.MM.DD hh:mm:ss"
    :rtype: str
    """
    return soup.find("span", class_="gall_date").get_text(strip=True)


def get_author_name_from_dom(soup: BeautifulSoup) -> str:
    author_sec = soup.find("div", class_="gall_writer")
    return author_sec.select_one(".nickname em").get_text(strip=True)


def get_author_link_from_dom(soup: BeautifulSoup) -> str:
    author_sec = soup.find("div", class_="gall_writer")
    on_click_action = author_sec.select_one(".writer_nikcon img")["onclick"]  # window.open('//gallog.dcinside.com/lx8j9twln1u5');
    return "https:" + re.match(r"window\.open\('(.+)'\);", on_click_action)[1]


def get_post_content_from_dom(soup: BeautifulSoup) -> str:
    return soup.find("div", class_="write_div").get_text(strip=True)


def get_filename(response: aiohttp.ClientResponse) -> str:
    # return response.content_disposition.filename  # BadContentDispositionHeader: attachment; filename=<file>.png. contains ";"
    return re.search(r"filename=(.+)", response.headers["Content-Disposition"])[1]


class Dcinside(Extractor):
    URL_REGEX = r"https://(?:gall|m).dcinside.com/[a-zA-Z/]*(?:\?id=|(?:board|m)/)(\w+)(?:&no=|/)(\d+)"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    @override
    def __str__(self):
        return "dcinside"

    @override
    async def get_all_media(self, webpage_url: UrlLike) -> Iterable[Media]:
        board_id, post_id = self.get_board_and_post_id(webpage_url)
        webpage_url = modify_webpage_url(board_id, post_id)
        soup = BeautifulSoup(
            await self.fetch_post_html(webpage_url),
            "lxml"
        )

        title = get_title_from_dom(soup)
        description = get_post_content_from_dom(soup)
        date = get_datetime_from_dom(soup)
        author_name = get_author_name_from_dom(soup)
        author_link = get_author_link_from_dom(soup)
        board_name = self.get_board_and_post_id(webpage_url)[0]

        for source_url in get_image_sources_from_dom(soup):
            tag: Tag = {
                "title": title,
                "description": description,
                "webpage_url": webpage_url,
                "source_url": source_url,
                "created_at": date,
                "artist": {
                    "display_name": author_name,
                    "webpage_url": author_link
                },
                "keywords": (board_name,)
            }

            headers = self.HEADERS.copy()
            headers["Referer"] = webpage_url
            async with self.session.get(source_url, headers=headers) as res:
                media = Media(
                    content=await res.content.read(),
                    filename=get_filename(res),
                    tags=tag
                )
                yield media

    async def fetch_post_html(self, webpage_url: UrlLike) -> bytes:
        async with self.session.get(webpage_url, headers=self.HEADERS) as res:
            res.raise_for_status()
            if not res.ok:
                logging.warning(f"Error occurred when fetching {webpage_url}. Error {res.status}")

            return await res.content.read()

    def get_board_and_post_id(self, webpage_url: UrlLike) -> tuple[str, str]:
        res = re.search(self.URL_REGEX, webpage_url)
        if not res:
            raise NotDcinsideLink(f"{webpage_url} is not a dcinside link.")
        return res[1], res[2]


if __name__ == "__main__":
    import asyncio
    import os
    # url = "https://gall.dcinside.com/m/projectmx/7579554"
    # url = "https://gall.dcinside.com/mgallery/board/view/?id=projectmx&no=7579554"
    url = "https://m.dcinside.com/board/projectmx/7579554"

    async def main():
        async with Dcinside() as dcinside:
            os.makedirs("./dcinside_media", exist_ok=True)
            async for media in dcinside.get_all_media(url):
                media.save("./dcinside_media", add_metadata=True)

    asyncio.run(main())
