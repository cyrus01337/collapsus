"""Explanation"""
import discord
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx, *, anything):
        """Explanation"""
        await ctx.send(discord.utils.escape_mentions(anything))


def setup(bot):
    bot.add_cog(Fun(bot))
