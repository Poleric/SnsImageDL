from discord import Intents
from discord.ext.commands import Bot

from snsimagedl_bot import commands
from snsimagedl_bot.config import AppConfig

__all__ = (
    "SnsImageDlBot",
)


class SnsImageDlBot(Bot):
    def __init__(self, *, config: AppConfig):
        super().__init__(
            intents=Intents.all(),
            command_prefix=config.bot.command_prefix,
        )
        self.config = config
        self.downloader = config.create_downloader()

    async def setup_hook(self) -> None:
        await self.add_cog(commands.General(self))
        await self.add_cog(commands.Downloader(self))

    # async def on_ready(self):
    #     logger.info(f"Logged in as {self.user}")
