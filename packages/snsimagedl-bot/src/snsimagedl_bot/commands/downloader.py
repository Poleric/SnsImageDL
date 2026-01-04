from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from discord import Message, VoiceChannel, TextChannel
from discord.ext import commands
from discord.ext.commands import Cog, Context

if TYPE_CHECKING:
    from snsimagedl_bot.bot import SnsImageDlBot

__all__ = (
    "Downloader",
)


class Downloader(Cog):
    def __init__(
            self,
            bot: SnsImageDlBot,
    ):
        self.bot = bot

    @Cog.listener("on_message")
    async def autosave(self, message: Message, /) -> None:
        if message.author == self.bot.user:
            return

        if message.channel.id not in self.bot.config.watch_channel_ids:
            return

        await self.bot.message_saver.save(message)
        await message.add_reaction("✅")

    @commands.hybrid_group()
    async def save(self, ctx: Context, message: Message) -> None:
        pass

    @save.command(name="url")
    async def save_url(self, ctx: Context, url: str) -> None:
        await self.bot.url_saver.save(url)
        await ctx.reply(f"Saved media.", ephemeral=True)

    @save.command(name="message")
    async def save_message(self, ctx: Context, message: Message) -> None:
        await self.bot.message_saver.save(message)
        await message.add_reaction("✅")
        await ctx.reply(f"Saved media.", ephemeral=True)

    @save.command(name="from")
    async def save_from(
            self,
            ctx: Context,
            channel: TextChannel | VoiceChannel | None = None,
            before: datetime | None = None,
            after: datetime | None = None
    ) -> None:
        channel = channel or ctx.channel

        async for message in channel.history(before=before, after=after):
            await self.bot.message_saver.save(message)
            await message.add_reaction("✅")

        await ctx.reply(f"Saved media.", ephemeral=True)

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
                "\n".join(self.bot.get_channel(channel_id).mention for channel_id in self.bot.config.watch_channel_ids),
                ephemeral=True
            )
        else:
            await ctx.reply("No channels.", ephemeral=True)

    @channel.command(name="remove")
    async def remove_channel(self, ctx: Context, channel: TextChannel | VoiceChannel | None = None) -> None:
        channel = channel or ctx.channel

        self.bot.config.watch_channel_ids.remove(channel.id)
        await ctx.reply(f"{channel.mention} is removed from the watch channel list.", ephemeral=True)
