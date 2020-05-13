"""Explanation"""
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def say(self, ctx, *, anything):
        """Explanation"""
        await ctx.send(anything)


def setup(bot):
    bot.add_cog(Fun(bot))
