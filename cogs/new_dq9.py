"""Explanation"""
import re

from collections.abc import Iterable
from typing import Any
from typing import Mapping

import aiohttp
from discord.ext import commands
from discord.ext import flags
from discord.ext import menus
from parsel import Selector

# import utils
import emojis
from constants import HEADERS


class Source(menus.ListPageSource):
    def __init__(self, entries, *args, **kwargs):
        super().__init__(entries, per_page=1, *args, **kwargs)

    async def format_page(self, menu, entry):
        current = menu.current_page + 1
        maximum = self.get_max_pages()
        return (f"**Page #{current} ({current}/{maximum})**\n\n"

                f"{entry}")


class DragonQuest9Cog(commands.Cog, name="Dragon Quest 9"):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False

        self.MIN_LEVEL = 1
        self.MIN_LOC = 1
        self.MAX_LEVEL = 99
        self.MAX_LOC = 150
        self.yab_site = "https://www.yabd.org/apps/dq9/grottosearch.php"
        self.SPECIAL = "Has a special floor"
        self.converters = (self._hex, int, str)
        self.data = {}
        self.cleanup_regex = re.compile(r"([\w\d\.\-:/() ]+)")

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

    def _hex(self, value: Any):
        n = int(value)
        if n <= 16:
            return n
        n = int(value, base=16)

        hex_str = str.upper(hex(n)[2:])
        return hex_str.zfill(4)

    def _is_special(self, data: tuple):
        try:
            return data[0] == self.SPECIAL
        except ValueError:
            return False

    def _create_grotto(self, data: Iterable):
        magic = 17
        ye = []

        for v in data:
            match_found = self.cleanup_regex.match(v)

            if match_found:
                stripped = str.strip(match_found.group(), "' ")

                if stripped != "":
                    for i, converter in enumerate(self.converters):
                        try:
                            converted = converter(stripped)
                        except Exception:
                            converted = None
                            continue
                        else:
                            if isinstance(converted, str):
                                if converted.find(":") > -1:
                                    continue
                                elif converted == self.SPECIAL:
                                    magic = 18
                                    ye.insert(0, converted)
                                else:
                                    ye.append(converted)
                            else:
                                ye.append(converted)
                            break
                        finally:
                            if len(ye) == magic:
                                yield tuple(ye)
                                magic = 17
                                ye = []
        if len(ye) > 0:
            yield tuple(ye)

    @flags.add_flag("--location", default=None)
    @flags.add_flag("--boss", default=None)
    @flags.add_flag("--type", dest="grotto_type", default=None)
    @flags.add_flag("--highest-hero-level", "-hhl", type=int, default=None)
    @flags.add_flag("--highest-hero-revocations", "-hhr",
                    type=int, default=None)
    @flags.add_flag("--last-grotto-level", "-lgr", type=int, default=None)
    @flags.command(aliases=["g"])
    async def grotto(self, ctx,
                     prefix, material,
                     suffix, level: int,
                     location=None, boss=None,
                     grotto_type=None, highest_hero_level: int = None,
                     max_revocs: int = None, last_grotto_level: int = None):
        """Explanation"""
        level, location = self.evaluate(level, location)
        prefix, envname, suffix = self.get_data_by(
            prefix=prefix,
            envname=material,
            suffix=suffix
        )
        keys = ("Seed", "Rank", "Name",
                "Boss", "Type", "Floors",
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
            "clev": highest_hero_level,
            "rev": max_revocs,
            "glev": last_grotto_level
        }

        for key, value in additional.items():
            if value is not None:
                params.setdefault(key, value)

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.post(self.yab_site, params=params) as response:
                if response.status != 200:
                    message = (f"Network error, report the following to the "
                               f"developer of this bot: ```py\n"
                               f"[{response.status}] - {response.message}\n"
                               f"```")
                else:
                    text = await response.text(encoding="ISO-8859-1")
                    selector = Selector(text=text)
                    selector.xpath('//div[@class="minimap"]').remove()
                    divs = selector.xpath('//div[@class="inner"]//text()')
                    grottos = divs.getall()
                    entries = []

                    for parsed in self._create_grotto(grottos):
                        message = ""

                        if self._is_special(parsed):
                            message += f"{emojis.STAR} **Special**\n"
                            parsed = parsed[1:]

                        for i, key, value in zip(range(len(parsed)), keys,
                                                 parsed):
                            if key == "Chests (S - I)":
                                value = (", ").join(map(str, parsed[i:i+10]))
                            message += (f"**{key}**: `{value}`\n")
                        message += (f"\n**Link**: <{response.url}>")
                        entries.append(str.strip(message))

                    if len(entries) == 1:
                        await ctx.send(entries[0])
                    else:
                        source = Source(entries)
                        menu = menus.MenuPages(source=source,
                                               clear_reactions_after=True,
                                               timeout=90.0)
                        await menu.start(ctx)


def setup(bot):
    bot.add_cog(DragonQuest9Cog(bot))
