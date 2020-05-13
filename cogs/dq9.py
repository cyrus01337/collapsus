"""Explanation"""
import aiohttp
from discord.ext import commands


class DragonQuest9Cog(commands.Cog, name="Dragon Quest 9"):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False

        self.yab_site = "https://www.yabd.org/apps/dq9/grottosearch.php"
        self.MIN_LEVEL = 1
        self.MIN_LOC = 1
        self.MAX_LEVEL = 99
        self.MAX_LOC = 150
        self.data = {}

        param_keys = ["prefix", "envname", "suffix"]

        for key in param_keys:
            with open(f"./resources/{key}", "r") as file:
                value = [l.strip() for l in file.readlines()]
                self.data.setdefault(key, value)

    def evaluate(self, level: int, location: int = None):
        ret = []

        if level >= self.MIN_LEVEL and level <= self.MAX_LEVEL:
            ret.append(level)
        else:
            raise commands.BadArgument("`level` must be greater than 0 and "
                                       "less than 100")

        if location is None:
            ret.append(location)
        else:
            location = int(location, 16)

            if location >= self.MIN_LOC and location <= self.MAX_LOC:
                ret.append(location)
            else:
                location = str.upper(hex(location))
                raise commands.BadArgument(f"`location` cannot be "
                                           f"{location[2:]}")
        return tuple(ret)

    def get_data_by(self, **kwargs):
        ret = []

        for key, value in kwargs.items():
            if value.isalpha():
                value = value.capitalize()
            elif value.isdigit() is False:
                try:
                    hex(value)
                except ValueError:
                    raise
                else:
                    value = value.upper()
            resource = self.data.get(key)
            index = resource.index(value) + 1
            ret.append(index)
        if len(ret) == 1:
            return ret[0]
        return tuple(ret)

    @commands.command()
    async def grotto(self, ctx, prefix, material, suffix, level: int,
                     location=None, boss=None, grotto_type=None,
                     max_level: int = None, max_revocations: int = None,
                     last_grotto_level: int = None):
        """Explanation"""
        level, location = self.evaluate(level, location)
        prefix, envname, suffix = self.get_data_by(
            prefix=prefix,
            envname=material,
            suffix=suffix
        )
        params = {
            "prefix": prefix,
            "envname": envname,
            "suffix": suffix,
            "level": level
        }
        other = {
            "loc": location,
            "boss": boss,
            "type": grotto_type,
            "clev": max_level,
            "rev": max_revocations,
            "glev": last_grotto_level
        }
        attribs = ["main", "grotto", "inner"]

        for key, value in other.items():
            if value is not None:
                params.setdefault(key, value)

        # params.setdefault("search", "Search")

        async with aiohttp.ClientSession() as session:
            async with session.post(self.yab_site, params=params) as response:
                await self.bot.send_embed(ctx, title="Grotto",
                                          desc=f"[URL]({response.url})")
        # await ctx.send(grotto)


def setup(bot):
    bot.add_cog(DragonQuest9Cog(bot))
