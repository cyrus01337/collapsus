import discord
from discord.ext import commands

from base import custom


class Fun(custom.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.allowed_mentions = discord.AllowedMentions.none()

    @commands.command()
    async def say(self, ctx, *, text):
        await ctx.send(text, allowed_mentions=self.allowed_mentions)


def setup(bot):
    bot.add_cog(Fun(bot))
