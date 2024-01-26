

from discord import CustomActivity, Intents, Message
from discord.ext import commands
from discord.ext.commands import Context

import re

from extractor import save_media, NotValidQuery
from extractor.exceptions import ScrapingException, MediaNotFound

import os
import sys
from setup_logging import setup_logger

logger = setup_logger()

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not BOT_TOKEN:
    logger.exception(
        "DISCORD_BOT_TOKEN is required. \n"
        "Set the bot token as an environment variable with the key `DISCORD_BOT_TOKEN`")
    sys.exit(1)


URL_REGEX = r"https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)"

bot = commands.Bot(
    command_prefix=".",
    activity=CustomActivity("Watching~"),
    intents=Intents.all(),

    description="Downloads any media embed in a message locally."
)


@bot.listen()
async def on_message(msg: Message):
    ctx: Context = await bot.get_context(msg)
    if ctx.valid:
        return

    urls = re.findall(URL_REGEX, msg.content)  # might be a url
    for url in urls:
        logger.debug(f"Url found. Attempting to save {url = }")
        try:
            await save_media(url)
        except NotValidQuery:
            logger.exception(f"{url=} is not supported.")
        except MediaNotFound:
            logger.exception(f"Media is not found in {url}.")
        except ScrapingException:
            logger.exception(f"Error encountered when saving {url}")
        else:  # no errors
            await msg.add_reaction("✅")


@bot.command()
async def save(ctx: Context, msg: Message):
    urls = re.findall(URL_REGEX, msg.content)
    for url in urls:
        logger.debug(f"Save command invoked: Saving {url = }")
        try:
            await save_media(url)
        except NotValidQuery:
            logging.exception(f"{url=} is not supported.")
            await ctx.reply(f"Saving {url} is not supported yet.")
            await msg.add_reaction("❓")
        except MediaNotFound:
            logging.exception(f"Media is not found in {url}.")
            await ctx.reply(f"No media is found for the url {url}")
            await msg.add_reaction("❌")
        except ScrapingException:  # so far should not be ran since theres no ScrapingException raises
            logging.exception(f"Error encountered when saving {url}")
            await ctx.reply(f"Error encountered when saving url {url}")
            await msg.add_reaction("❌")
        else:  # no errors
            await ctx.message.add_reaction("✅")
            await msg.add_reaction("✅")


async def main():
    await bot.start(BOT_TOKEN)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
