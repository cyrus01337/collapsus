"""Explanation"""
import typing

from discord.ext import commands

import emojis


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = {
            "chest": ("SABCDEFGHI")[::-1],
            "grotto": ("SABCDEFGHIJK")[::-1]
        }

    async def _resolve(self, ctx, medium: str, index: typing.Union[int, str]):
        medium = medium.lower()
        data = self.data.get(medium)
        message = "**Rank**: `{letter} ({number})`"

        if medium not in self.data.keys():
            return

        if isinstance(index, int) and index > 0 and index < 13:
            letter = data[index-1]
            message = message.format(letter=letter, number=index)
        elif isinstance(index, str):
            index = index.upper()

            if index not in data:
                return
            number = data.index(index) + 1
            message = message.format(letter=index, number=number)
        else:
            return
        await ctx.send(message)

    @commands.command(name="prefix")
    async def _prefix(self, ctx):
        """Explanation"""
        await ctx.send(f"The prefix is `{ctx.prefix}` or you can mention "
                       f"me! E.g. `{ctx.prefix} ping` or "
                       f"{self.bot.user.mention}` ping`")

    @commands.command()
    async def ping(self, ctx):
        """Explanation"""
        await ctx.send(f"{emojis.PING_PONG} **Pong!** "
                       f"{int(self.bot.latency * 1000):,}ms.")

    @commands.group(invoke_without_subcommand=True)
    async def resolve(self, ctx, medium, index: typing.Union[int, str]):
        """Explanation"""
        await self._resolve(ctx, medium=medium, index=index)


def setup(bot):
    bot.add_cog(Information(bot))
