import parsel

import aiohttp
from discord.ext import commands

from base import custom
from objects import Flags


class DragonQuest9(custom.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.URL = "https://www.yabd.org/apps/dq9/grottosearch.php"

    @commands.command(aliases=["g"])
    async def grotto(self,
                     ctx,
                     prefix: Flags.PREFIX.converter,
                     material: Flags.ENVNAME.converter,
                     suffix: Flags.SUFFIX.converter,
                     level: Flags.LEVEL.converter):
        await ctx.send(f"prefix={prefix!r}, material={material!r}, "
                       f"suffix={suffix!r}, level={level!r}")


def setup(bot):
    bot.add_cog(DragonQuest9(bot))
