import random
import re

import discord
from discord.ext import commands
from jishaku.functools import executor_function


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.allowed_mentions = discord.AllowedMentions.none()
        self.roll_regex = re.compile(r"(?P<times>[0-9]+)[d](?P<sides>[0-9]+)")

    @executor_function
    def _do_roll(self, times: int, sides: int):
        result = 0

        if sides == 1:
            return sides * times

        for _ in range(times):
            result += random.randint(1, sides)
        return result

    @commands.command()
    async def say(self, ctx, *, text):
        await ctx.send(text, allowed_mentions=self.allowed_mentions)

    @commands.command()
    async def roll(self, ctx, die):
        match_found = self.roll_regex.fullmatch(die)

        if not match_found:
            return

        times = int(match_found.group("times"))
        sides = int(match_found.group("sides"))

        if 0 in (times, sides):
            return

        result = await self._do_roll(times, sides)

        await ctx.send(
            f"**Rolled a d{sides:,}, {times:,} time(s)\n"
            f"Result: `{result:,}`**"
        )


def setup(bot):
    bot.add_cog(Fun(bot))
