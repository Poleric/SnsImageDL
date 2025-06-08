import asyncio
import logging
import os
import re
import traceback
from typing import override, Iterable, AsyncGenerator

from pathlib import Path
import aiohttp
from discord import Intents, Message, TextChannel, VoiceChannel
from discord.ext.commands import Bot, Context
from discord.ext.commands.errors import CommandError
from discord.utils import setup_logging

from sns_image_dl.exceptions import UnsupportedLink
from sns_image_dl.extractor import Extractor, Pixiv, Twitter, Dcinside
from sns_image_dl.tagging import Tagger, ExifTagger, JpegCommentTagger, XmpTagger
from sns_image_dl.media import Media

setup_logging()
logger = logging.getLogger("image-dl-bot")


class ImageDLBot(Bot):
    URL_REGEX: re.Pattern = re.compile(
        r"https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_+.~#?&/=]*")

    def __init__(
            self,
            output_directory: Path,
            *args,
            channel_ids: set[int] = None,
            **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.extractors: list[Extractor] = []
        self.taggers: list[Tagger] = [ExifTagger(), JpegCommentTagger(), XmpTagger()]
        self.session: aiohttp.ClientSession | None = None

        # configurable
        self.channel_ids: set[int] = channel_ids or set()
        self.output_directory = output_directory

    # noinspection PyBroadException
    @override
    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

        # initialize the extractors
        try:
            self.extractors.append(Twitter(self.session))
        except Exception:
            logger.warning("Failed to load Twitter extractor.", exc_info=True)

        try:
            refresh_token = os.getenv("PIXIV_REFRESH_TOKEN")
            assert refresh_token, "Environment variable PIXIV_REFRESH_TOKEN is not set."

            self.extractors.append(Pixiv(refresh_token=refresh_token))
        except Exception:
            logger.warning("Failed to load Pixiv extractor.", exc_info=True)

        try:
            self.extractors.append(Dcinside())
        except Exception:
            logger.warning("Failed to load Dcinside extractor.", exc_info=True)

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    @override
    async def close(self) -> None:
        await super().close()
        await self.session.close()

    @override
    async def on_command_error(self, ctx: Context, exc: CommandError, /) -> None:
        logger.error(
            f'Ignoring exception in command {ctx.command}:\n'
            f'{"".join(traceback.format_exception(type(exc), exc, exc.__traceback__))}'
        )

    def save_locally(self, extractor: type[Extractor], media: Media) -> None:
        output_path = self.output_directory

        match extractor:  # noqa
            case Twitter():
                output_path /= "twitter"
            case Pixiv():
                output_path /= "pixiv"
            case Dcinside():
                output_path /= "dcinside"
            case _:
                output_path /= extractor.__name__.casefold()

        output_path.mkdir(exist_ok=True, parents=True)

        output_path /= media.metadata["filename"]

        with output_path.open("wb") as f:
            content = media.content

            for tagger in self.taggers:
                if not tagger.is_extension_supported(output_path.suffix):
                    continue

                content = tagger.tag(content, media.metadata)

            f.write(content)


    async def process(self, url: str, /) -> list[Media]:
        async def _process() -> AsyncGenerator[Media]:
            for extractor in self.extractors:
                if not extractor.is_link_supported(url):
                    continue

                async for media in extractor.extract(url):
                    self.save_locally(extractor, media)

                    yield media

        processed = []
        async for media in _process():
            processed.append(media)
        return processed


command_prefix = os.getenv("COMMAND_PREFIX") or "."
logger.info(f"Command prefix set to {command_prefix}")

output_directory = os.getenv("OUTPUT_DIRECTORY")
if not output_directory:
    output_directory = "./media"
    logger.warning(f"OUTPUT_DIRECTORY not specified. Defaulting to {output_directory}")
else:
    logger.info(f"Output directory set to {output_directory}")

if os.getenv("CHANNEL_IDS"):
    channel_ids = set(int(id) for id in os.getenv("CHANNEL_IDS").split(","))
    logger.info(f"Watching the following channels: " + ", ".join(str(id) for id in channel_ids))
else:
    channel_ids = set()
    logger.info("Not watching any channel. Set the channels to watch with `channel add`")


bot = ImageDLBot(
    intents=Intents.all(),
    command_prefix=command_prefix,
    output_directory=Path(output_directory),
    channel_ids=channel_ids
)


@bot.hybrid_command()
async def sync(ctx: Context, globally: bool = False):
    if globally:
        await bot.tree.sync()
    else:
        await bot.tree.sync(guild=ctx.guild)
    await ctx.reply("Syncing...", ephemeral=True)


@bot.listen("on_message")
async def autosave(message: Message, /) -> None:
    if message.author == bot.user:
        return

    urls = bot.URL_REGEX.findall(message.content)
    if not urls:
        return

    if message.channel.id not in bot.channel_ids:
        return

    processed: list[Media] = []
    failed: list[tuple[str, Exception]] = []
    for url in urls:
        try:
            processed.extend(await bot.process(url))
        except Exception as e:
            logger.exception(f"Couldn't save {url}")
            failed.append((url, e))

    if processed:
        await message.add_reaction("✅")
    if failed:
        await message.add_reaction("❌")


@bot.hybrid_command()
async def save(ctx: Context, message: Message):
    urls = bot.URL_REGEX.findall(message.content)
    if not urls:
        await ctx.reply("There is no media to save.", ephemeral=True)
        return

    processed: list[Media] = []
    failed: list[tuple[str, Exception]] = []
    for url in urls:
        try:
            saved = await bot.process(url)

            if saved:
                processed.extend(saved)
            else:
                failed.append((url, UnsupportedLink()))
        except Exception as e:
            logger.exception(f"Couldn't save {url}")
            failed.append((url, e))

    if processed:
        await message.add_reaction("✅")
        await ctx.reply(f"Saved {len(processed)} media.", ephemeral=True)
    if failed:
        await message.add_reaction("❌")
        await ctx.reply("Failed to save:\n" + "\n".join(f"<{url}> ({e})" for url, e in failed))


@bot.hybrid_group(name="channel")
async def watch_channel(ctx: Context):
    if not ctx.invoked_subcommand:
        await list_channels(ctx)


@watch_channel.command(name="add")
async def add_channel(ctx: Context, channel: TextChannel | VoiceChannel | None = None):
    channel = channel or ctx.channel
    bot.channel_ids.add(channel.id)

    await ctx.reply(f"{channel.mention} added to the watch channel list.", ephemeral=True)


@watch_channel.command(name="list")
async def list_channels(ctx: Context):
    if bot.channel_ids:
        await ctx.reply("Watching channels:\n" +
                        "\n".join(bot.get_channel(channel_id).mention for channel_id in bot.channel_ids),
                        ephemeral=True)
    else:
        await ctx.reply("No channels.")


@watch_channel.command(name="remove")
async def remove_channel(ctx: Context, channel: TextChannel | VoiceChannel | None = None):
    channel = channel or ctx.channel
    bot.channel_ids.remove(channel.id)

    await ctx.reply(f"{channel.mention} is removed from the watch channel list.", ephemeral=True)


if __name__ == '__main__':
    async def main():
        bot_token = os.getenv("DISCORD_BOT_TOKEN")
        assert bot_token, "Environment variable DISCORD_BOT_TOKEN is not specified. Please set the variable with the bot token."

        await bot.start(bot_token)


    asyncio.run(main())
