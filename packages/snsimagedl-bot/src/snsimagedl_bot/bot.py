from discord import Message
from discord.ext.commands import Bot

from snsimagedl_bot import commands
from snsimagedl_bot.config import BotConfig
from snsimagedl_bot.saver import Saver

__all__ = (
    "SnsImageDlBot",
)


class SnsImageDlBot(Bot, Saver[Message], Saver[str]):
    def __init__(self, config: BotConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = config

    async def setup_hook(self) -> None:
        await self.add_cog(commands.Downloader(self))
        await self.add_cog(commands.General(self))

    # async def on_ready(self):
    #     logger.info(f"Logged in as {self.user}")
