"""Explanation"""
from discord.ext import commands

import emojis
import prefix


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Explanation"""
        await ctx.send(f"{emojis.PING_PONG} **Pong!** "
                       f"{int(self.bot.latency * 1000):,}ms.")

    @commands.command(name="prefix")
    async def _prefix(self, ctx):
        """Explanation"""
        await ctx.send(f"The prefix is `{prefix.DEFAULT}` or you can mention "
                       f"me! E.g. `{prefix.DEFAULT} ping` or "
                       f"{self.bot.mention}` ping`")


def setup(bot):
    bot.add_cog(Information(bot))
