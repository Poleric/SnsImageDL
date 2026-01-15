import asyncio

import aiohttp
from discord.utils import setup_logging

from snsimagedl_bot import SnsImageDlBot
from snsimagedl_bot.config import AppConfig, set_global_session


async def main():
    setup_logging()

    config_path = "./config.json"

    async with aiohttp.ClientSession() as session:
        set_global_session(session)

        config = AppConfig.from_config(config_path)
        bot = SnsImageDlBot(config=config)

        await bot.start(config.bot.token)


if __name__ == '__main__':
    asyncio.run(main())
