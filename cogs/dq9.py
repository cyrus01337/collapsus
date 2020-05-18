"""Explanation"""
import re
from collections.abc import Iterable
from typing import Any
from typing import Callable
from typing import Mapping

import aiohttp
from discord.ext import commands
from parsel import Selector

# import utils


class DragonQuest9Cog(commands.Cog, name="Dragon Quest 9"):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False

        self.MIN_LEVEL = 1
        self.MIN_LOC = 1
        self.MAX_LEVEL = 99
        self.MAX_LOC = 150
        self._magic = 17
        self.yab_site = "https://www.yabd.org/apps/dq9/grottosearch.php"
        self.converters = (self.hex, int, str)
        self.data = {}
        self.regex = re.compile(r"([\w\d\.\- /()]+)")

        param_keys = ["prefix", "envname", "suffix"]

        for key in param_keys:
            with open(f"./resources/{key}", "r") as file:
                value = [line.strip() for line in file.readlines()]
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
            location = int(location, base=16)

            if location >= self.MIN_LOC and location <= self.MAX_LOC:
                ret.append(location)
            else:
                location = str.upper(hex(location))
                raise commands.BadArgument(f"`location` cannot be "
                                           f"{location[2:]}")
        return tuple(ret)

    def get_data_by(self, **kwargs: Mapping):
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

    def convert_to(self, value: Any, converter: Callable):
        try:
            return converter(value)
        except Exception:
            return value

    def get_class(self, selector: Selector, *names: str):
        ret = []

        for name in names:
            xpath = selector.xpath(f'//div[@class="{name}"]/text()')
            elements = xpath.getall()
            ret.append(elements)
        return tuple(ret)

    def hex(self, value: Any):
        n = int(value, base=16)
        if n < 17:
            return n

        hex_str = str.upper(hex(n)[2:])
        return hex_str.zfill(4)

    # rename, turn into generator that iterates through all characters
    # of the given iterable and yields it as a converted tuple once the
    # length of it reaches self._magic - create as little memory as
    # functionally possible
    def _create_parseable(self, data: Iterable):
        ye = []

        for v in data:
            match_found = self.regex.match(v)

            if match_found:
                stripped = str.strip(match_found.group(), "' ")

                if stripped != "":
                    for converter in self.converters:
                        try:
                            converted = converter(stripped)
                        except Exception:
                            converted = None  # temp
                            # continue
                        else:
                            ye.append(converted)
                            break
                        finally:
                            if len(ye) == self._magic:
                                yield tuple(ye)
                                ye = []
        if len(ye) > 0:
            yield tuple(ye)

    @commands.command(usage="Granite Tunnel Woe 1 2D")
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
        keys = ("Seed", "Rank", "Name", "Boss", "Type", "Floors",
                "Monster Rank", "Chests (S - I)")

        params = {
            "prefix": prefix,
            "envname": envname,
            "suffix": suffix,
            "level": level,
            "search": "Search"
        }
        additional = {
            "loc": location,
            "boss": boss,
            "type": grotto_type,
            "clev": max_level,
            "rev": max_revocations,
            "glev": last_grotto_level
        }

        for key, value in additional.items():
            if value is not None:
                params.setdefault(key, value)

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(self.yab_site, params=params) as response:
                if response.status != 200:
                    message = (f"Network error, report the following to the "
                               f"developer of this bot: ```py\n"
                               f"[{response.status}] - {response.message}\n"
                               f"```")
                else:
                    text = await response.text(encoding="ISO-8859-1")
                    selector = Selector(text=text)
                    grottos, locations, attributes = self.get_class(
                        selector,
                        "inner",
                        "minimap",
                        "special"
                    )
                    # assign to "grottos found: n" from website
                    message = ""

                    for parsed in self._create_parseable(grottos):
                        for i, key, value in zip(range(len(parsed)), keys,
                                                 parsed):
                            if key == "Chests (S - I)":
                                value = (", ").join(map(str, parsed[i:i+10]))
                            message += (f"**{key}**: `{value}`\n")
                        message += "\n"
                    message += f"**Link**: {response.url}"

                    if len(message) > 2000:
                        message = (f"`Message > 2,000 characters, refer to "
                                   f"link below`\n\n"

                                   f"{response.url}")
                await ctx.send(message)
                # await self.bot.send_embed(ctx, response.url,
                #                           title="Grotto",
                #                           desc=f"[URL]({response.url})")


def setup(bot):
    bot.add_cog(DragonQuest9Cog(bot))
