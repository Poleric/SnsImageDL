import asyncio
from pathlib import Path

import aiohttp
import msgspec.json
from discord import Intents
from discord.utils import setup_logging

import config as app_config
from config import AppConfig
from snsimagedl_bot.bot import SnsImageDlBot


async def main():
    setup_logging()
    config_path = Path("./config.json")

    async with aiohttp.ClientSession() as session:
        app_config.session = session

        config = msgspec.json.decode(config_path.read_bytes(), type=AppConfig)

        bot = SnsImageDlBot(
            watch_channel_ids=config.watch_channel_ids,
            output_directory=Path(config.output_directory),
            downloader=config.downloader,
            intents=Intents.all(),
            command_prefix=config.bot.command_prefix,
        )

        await bot.start(config.bot.token)


if __name__ == '__main__':
    asyncio.run(main())
