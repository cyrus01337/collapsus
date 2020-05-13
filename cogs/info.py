"""Explanation"""
from discord.ext import commands

import emojis


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Explanation"""
        await ctx.send(f"{emojis.PING_PONG} **Pong!** "
                       f"{int(self.bot.latency * 1000):,}ms.")


def setup(bot):
    bot.add_cog(Information(bot))
