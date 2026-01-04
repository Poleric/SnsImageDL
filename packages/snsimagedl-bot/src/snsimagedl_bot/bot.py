import re
from pathlib import Path
from typing import override, ClassVar

from discord import Message
from discord.ext.commands import Bot

from snsimagedl_bot import commands
from snsimagedl_bot.config import BotConfig
from snsimagedl_bot.saver import Saver
from snsimagedl_lib import MediaDownloader

__all__ = (
    "SnsImageDlBot",
)


class SnsImageDlBot(Bot, Saver[Message], Saver[str]):
    def __init__(self, config: BotConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = config
        self.url_saver = self.UrlSaver(self.config.output_directory, self.config.downloader)
        self.message_saver = self.MessageSaver(self.url_saver)

    async def setup_hook(self) -> None:
        await self.add_cog(commands.Downloader(self))
        await self.add_cog(commands.General(self))

    # async def on_ready(self):
    #     logger.info(f"Logged in as {self.user}")

    class UrlSaver(Saver[str]):
        def __init__(self, output_dir: Path, downloader: MediaDownloader):
            self.output_dir = output_dir
            self.downloader = downloader

        @override
        async def save(self, message: str, /) -> None:
            async for result in self.downloader.query(message):
                result.save_to(
                    self.output_dir / result.extractor.__class__.__name__.casefold() / result.metadata.filename)

    class MessageSaver(Saver[Message]):
        URL_PATTERN: ClassVar[re.Pattern] = re.compile(
            r"https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_+.~#?&/=]*"
        )

        def __init__(self, url_saver: Saver[str]):
            self.url_saver = url_saver

        @override
        async def save(self, message: Message, /) -> None:
            urls = self.URL_PATTERN.findall(message.content)

            for url in urls:
                await self.url_saver.save(url)
