import os

import discord
from discord.ext import commands
from discord.ext.commands import Context
import logging
import sys
import re

from extractor import save_media, NotValidQuery
from extractor.exceptions import ScrapingException, MediaNotFound


URL_REGEX = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not BOT_TOKEN:
    logging.exception("DISCORD_BOT_TOKEN is required. Set the bot token as an environment variable with the key DISCORD_BOT_TOKEN")
    sys.exit()

discord.utils.setup_logging()
bot = commands.Bot(
    command_prefix=".",
    activity=discord.CustomActivity("Watching~"),
    intents=discord.Intents.all(),

    description="Downloads any media embed in a message locally."
)


@bot.listen()
async def on_message(msg: discord.Message):
    url = re.search(URL_REGEX, msg.content)  # might be a url
    if url:
        try:
            save_media(url[0])
        except MediaNotFound:
            logging.exception(f"Media is not found {url}.")
            await msg.add_reaction("❌")
        except ScrapingException:
            logging.exception(f"Error encountered when saving {url}")
            await msg.add_reaction("❌")
        else:  # no errors
            await msg.add_reaction("✅")


@bot.command()
async def save(ctx: Context, msg: discord.Message):
    url = re.search(URL_REGEX, msg.content)[0]

    try:
        save_media(url)
    except NotValidQuery:
        logging.exception(f"Saving {url} is not supported yet.")
        await msg.add_reaction("❓")
    except MediaNotFound:
        logging.exception(f"Media is not found {url}.")
        await msg.add_reaction("❌")
    except ScrapingException:
        logging.exception(f"Error encountered when saving {url}")
        await msg.add_reaction("❌")
    else:  # no errors
        await msg.add_reaction("✅")


async def main():
    await bot.start(BOT_TOKEN)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
