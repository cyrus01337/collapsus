"""Explanation"""
import re

# import aiohttp
# import discord
from discord.ext import commands

from constants import Owner


class TestingCog(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = True

        self.grotto_regex = re.compile(
            r"(?P<prefix>Basalt|Bronze|Clay|Copper|Diamond|Emerald|Gold|"
            r"Granite|Graphite|Iron|Platinum|Rock|Ruby|Sapphire|Silver|Steel)"
            r"\s+"
            r"(?P<environ>Abyss|Cave|Chasm|Crater|Crevasse|Crypt|Dungeon|"
            r"Glacier|Icepit|Lair|Lake|Marsh|Maze|Mine|Moor|Nest|Path|Ruins|"
            r"Snowhall|Tundra|Tunnel|Void|Waterway|World)\s+"
            r"(?:of\s+)?"
            r"(?P<suffix>Bane|Bliss|Death|Dolour|Doom|Doubt|Dread|Evil|Fear|"
            r"Glee|Gloom|Hurt|Joy|Regret|Ruin|Woe)\s+"
            r"(?:Lv\.?\s+|Level\s+|L\s*)?"
            r"(?P<level>[1-9][0-9]?\b)"
            r"(?:\s+(?=[A-F0-9]{1,2}\b)(?P<location>0?[1-9A-F]|[1-8][0-9A-F]|"
            r"9[0-6])\b)?"
            r"(?:\s+(?P<boss>Equinox|Nemean|Shogum|Trauminator|Elusid|Sir|"
            r"Atlas|Hammibal|Fowleye|Excalipurr|Tyrannosaurus|Greygnarl)\b)?"
            r"(?:\s+(?P<type>Caves|Fire|Ice|Ruins|Water))?"
            r"(?:\s+(?P<max_level>[1-9][0-9]?)\b)?"
            r"(?:\s+(?P<max_revocations>10|[0-9])\b)?"
            r"(?:\s+(?P<max_grotto_level>[1-9][0-9]?)\b)?"
            r"$",
            flags=re.IGNORECASE + re.VERBOSE
        )

    async def _default(self, ctx):
        await ctx.send("Working!")

    async def cog_check(self, ctx):
        return ctx.author.id == Owner.CYRUS.value

    @commands.group(invoke_without_subcommand=True)
    async def test(self, ctx, *, query):
        # await self._default(ctx)
        await ctx.send(f"```\n"
                       f"{query}\n"
                       f"{self.grotto_regex.match(query)}\n"
                       f"```")

    @test.group()
    async def outer(self, ctx, *args, **kwargs):
        await self._default(ctx)

    @outer.command()
    async def inner(self, ctx, *args, **kwargs):
        await self._default(ctx)


def setup(bot):
    bot.add_cog(TestingCog(bot))
