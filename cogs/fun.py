"""Explanation"""
import random
import re

import discord
from discord.ext import commands, flags

import utils


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roll_regex = re.compile(r"^(?P<amount>\d+)[dD](?P<sides>\d+)$")

    @commands.command()
    async def say(self, ctx, *, anything):
        """Explanation"""
        await ctx.send(discord.utils.escape_mentions(anything))

    @flags.add_flag("--log", "-l", action="store_true")
    @flags.command()
    async def roll(self, ctx, query, **flags):
        query_valid = self.roll_regex.fullmatch(query)

        if query_valid:
            rolls = []
            amount = int(query_valid.group("amount"))
            sides = int(query_valid.group("sides"))

            if 0 in (amount, sides) or amount > 20 or sides > 100:
                return

            for _ in range(amount):
                rolls.append(random.randint(1, sides))
            message = (f"**Rolled a d{sides} {amount} time(s)\n"
                       f"Result: `{sum(rolls):,}`**\n")

            if flags.get("log"):
                mystbin = await utils.mystbin((" + ").join(map(str, rolls)))
                message += f"<{mystbin}>"
            await ctx.send(message)


def setup(bot):
    bot.add_cog(Fun(bot))
