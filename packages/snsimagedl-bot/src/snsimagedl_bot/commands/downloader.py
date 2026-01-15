from __future__ import annotations

import re
from typing import TYPE_CHECKING, Collection, ClassVar

from discord import Message, VoiceChannel, TextChannel, Embed
from discord.ext import commands
from discord.ext.commands import Cog, Context

from snsimagedl_bot.formatter import FilePathFormatter, FilePathContext
from snsimagedl_lib import QueryResult

if TYPE_CHECKING:
    from snsimagedl_bot.bot import SnsImageDlBot

__all__ = (
    "Downloader",
)


class Downloader(Cog):
    URL_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_+.~#?&/=]*"
    )

    def __init__(
            self,
            bot: SnsImageDlBot,
    ):
        self.bot = bot
        self.path_formatter = FilePathFormatter()

    async def _query(self, message: Message, /) -> Collection[QueryResult]:
        urls = self.URL_PATTERN.findall(message.content)

        results = []
        for url in urls:
            for result in await self.bot.downloader.query(url):
                results.append(result)
        return results

    async def _save(self, results: Collection[QueryResult]) -> None:
        for result in results:
            path = self.path_formatter.compile_path(
                self.bot.config.output_directory,
                context=FilePathContext.from_query(result)
            )
            path.parent.mkdir(exist_ok=True, parents=True)

            (await result.download()) \
                .tag() \
                .save_to(path)

    @staticmethod
    def _get_success_embed(results: Collection[QueryResult]) -> Embed:
        embed = Embed(title="Success")
        embed.add_field(name="Downloaded:", value="\n".join(
            f"[{result.metadata.filename}]({result.metadata.source_url})" for result in results))

        return embed

    @Cog.listener("on_message")
    async def autosave(self, message: Message, /) -> None:
        if message.author == self.bot.user:
            return

        if message.channel.id not in self.bot.config.watch_channel_ids:
            return

        results = await self._query(message)
        if results:
            await self._save(results)
            await message.add_reaction("✅")
        else:
            await message.add_reaction("❌")

    @commands.hybrid_group()
    async def save(self, ctx: Context, message: Message | None = None) -> None:
        if not ctx.invoked_subcommand and message is not None:
            await self.save_message(ctx, message)

    @save.command(name="url")
    async def save_url(self, ctx: Context, url: str) -> None:
        results = await self.bot.downloader.query(url)
        if results:
            await self._save(results)

            embed = self._get_success_embed(results)
            await ctx.reply(embed=embed, ephemeral=True)
        else:
            await ctx.reply("No media found.", ephemeral=True)

    @save.command(name="message")
    async def save_message(self, ctx: Context, message: Message) -> None:
        results = await self._query(message)
        if results:
            await self._save(results)
            await message.add_reaction("✅")

            embed = self._get_success_embed(results)
            await ctx.reply(embed=embed, ephemeral=True)
        else:
            await message.add_reaction("❌")
            await ctx.reply("No media found.", ephemeral=True)

    @save.command(name="from")
    async def save_from(
            self,
            ctx: Context,
            channel: TextChannel | VoiceChannel | None = None,
            before: Message | None = None,
            after: Message | None = None
    ) -> None:
        channel = channel or ctx.channel

        all_results = []
        async for message in channel.history(before=before, after=after):
            results = await self._query(message)
            if results:
                await self._save(results)
                await message.add_reaction("✅")

                all_results.extend(results)
            else:
                await message.add_reaction("❌")

        if all_results:
            embed = self._get_success_embed(all_results)
            await ctx.reply(embed=embed, ephemeral=True)
        else:
            await ctx.reply("No media found.", ephemeral=True)

    @commands.hybrid_group()
    async def channel(self, ctx: Context) -> None:
        if not ctx.invoked_subcommand:
            await self.list_channels(ctx)

    @channel.command(name="add")
    async def add_channel(self, ctx: Context, channel: TextChannel | VoiceChannel | None = None) -> None:
        channel = channel or ctx.channel

        self.bot.config.watch_channel_ids.add(channel.id)
        await ctx.reply(f"{channel.mention} added to the watch channel list.", ephemeral=True)

    @channel.command(name="list")
    async def list_channels(self, ctx: Context) -> None:
        if self.bot.config.watch_channel_ids:
            await ctx.reply(
                "Watching channels:\n" +
                "\n".join(self.bot.get_channel(channel_id).mention for channel_id in self.bot.watch_channel_ids),
                ephemeral=True
            )
        else:
            await ctx.reply("No channels.", ephemeral=True)

    @channel.command(name="remove")
    async def remove_channel(self, ctx: Context, channel: TextChannel | VoiceChannel | None = None) -> None:
        channel = channel or ctx.channel

        self.bot.config.watch_channel_ids.remove(channel.id)
        await ctx.reply(f"{channel.mention} is removed from the watch channel list.", ephemeral=True)
