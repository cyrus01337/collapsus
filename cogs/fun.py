"""Explanation"""
import random
import re

import discord
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roll_regex = re.compile(r"^(?P<amount>\d+)[dD](?P<sides>\d+)$")

    @commands.command()
    async def say(self, ctx, *, anything):
        """Explanation"""
        await ctx.send(discord.utils.escape_mentions(anything))

    @commands.command()
    async def roll(self, ctx, query):
        query_valid = self.roll_regex.fullmatch(query)

        if query_valid:
            rolls = []
            iterations = range(int(query_valid.group("amount")))
            sides = int(query_valid.group("sides"))

            for _ in iterations:
                rolls.append(random.randint(1, sides))
            joined = (" + ").join(rolls)
            await ctx.send(f"`{joined}`\n\n"

                           f"**Result: {sum(rolls)}**")


def setup(bot):
    bot.add_cog(Fun(bot))
