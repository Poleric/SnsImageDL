from discord.ext import commands
from discord.ext.commands import Cog, Context, Bot

__all__ = (
    "General",
)


class General(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: Context, globally: bool = False):
        if globally:
            await self.bot.tree.sync()
        else:
            await self.bot.tree.sync(guild=ctx.guild)

        await ctx.reply("Syncing...", ephemeral=True)
