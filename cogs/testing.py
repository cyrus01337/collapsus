"""Explanation"""
# import aiohttp
# import discord
from discord.ext import commands

from constants import Owner


class TestingCog(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = True

    async def _default(self, ctx):
        await ctx.send("Working!")

    async def cog_check(self, ctx):
        return ctx.author.id == Owner.DJ.value

    @commands.group(invoke_without_subcommand=True)
    async def test(self, ctx, *args, **kwargs):
        await self._default(ctx)

    @test.group()
    async def outer(self, ctx, *args, **kwargs):
        await self._default(ctx)

    @outer.command()
    async def inner(self, ctx, *args, **kwargs):
        await self._default(ctx)


def setup(bot):
    bot.add_cog(TestingCog(bot))
