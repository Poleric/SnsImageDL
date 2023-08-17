import discord
from discord.ext import commands
import logging

from extractor import save_media, NotValidQuery
from extractor.exceptions import ScrapingException


discord.utils.setup_logging()
bot = commands.Bot(
    command_prefix=".",
    activity=discord.CustomActivity("Watching~"),
    intents=discord.Intents.all(),

    description="Downloads any media embed in a message locally."
)


@bot.listen()
async def on_message(msg: discord.Message):
    ctx = await bot.get_context(msg)
    await ctx.invoke(save, msg=msg)


@commands.command()
async def save(ctx, msg: discord.Message):
    clean_content = msg.content.strip("<>|\"")

    try:
        save_media(clean_content)
    except NotValidQuery:
        logging.exception(f"Saving {clean_content} is not supported yet.")
        await msg.add_reaction("❓")
    except ScrapingException:
        logging.exception(f"Error encountered when saving {clean_content}")
        await msg.add_reaction("❌")
    else:  # no errors
        await msg.add_reaction("✅")


async def main():
    await bot.start("ODE0MDE0MDkzODc3OTY4ODk3.YDXrsw.98uponQ0gPtP3aLxmRCZWnf6JR8")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
