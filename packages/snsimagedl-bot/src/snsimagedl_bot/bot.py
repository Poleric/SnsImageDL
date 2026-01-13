from pathlib import Path

from discord.ext.commands import Bot

from snsimagedl_bot import commands

__all__ = (
    "SnsImageDlBot",
)

from snsimagedl_lib import MediaDownloader


class SnsImageDlBot(Bot):
    def __init__(
            self,
            watch_channel_ids: set[int],
            output_directory: Path,
            downloader: MediaDownloader,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.watch_channel_ids = watch_channel_ids
        self.output_directory = output_directory
        self.downloader = downloader

    async def setup_hook(self) -> None:
        await self.add_cog(commands.General(self))
        await self.add_cog(commands.Downloader(self))

    # async def on_ready(self):
    #     logger.info(f"Logged in as {self.user}")
