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
        # 17 should work for singles
        # 18 should work with special attributes
        # 19 works for singles
        # 20 should work for singles with special attributes pre-testing
        self._magic = 19  # set to 17
        self.yab_site = "https://www.yabd.org/apps/dq9/grottosearch.php"
        self.mystbin = "https://mystb.in"
        self.data = {}
        self.headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; "
                           "rv:76.0) Gecko/20100101 Firefox/76.0,"),
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }
        self.regex = re.compile(r"([\w\d\./()\- ]+)")

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

    def _parse_grotto(self, data: list):
        ret = []

        for i, d in enumerate(data):
            converters = (int, str) if i > 0 else (str,)
            resolved = self.regex.match(d)

            if resolved is not None:
                group = str.strip(resolved.group(), "' ")

                if group == "":
                    continue
                for converter in converters:
                    try:
                        converted = converter(group)
                    except Exception:
                        continue
                    else:
                        ret.append(converted)
                        break
        return tuple(ret)

    async def hastebin(self, message: str):
        url = f"{self.mystbin}/documents"

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, data=message) as response:
                json = await response.json()
                key = json.get("key")
                return f"{self.mystbin}/{key}"

    @commands.command(usage="Granite Tunnel Woe 1 2D")
    async def grotto(self, ctx, prefix, material, suffix, level: int,
                     location=None, boss=None, grotto_type=None,
                     max_level: int = None, max_revocations: int = None,
                     last_grotto_level: int = None):
        """Explanation"""
        level, location = self.evaluate(level, location)
        keys = ("Seed", "Rank", "Name", "Boss", "Type", "Floors",
                "Monster Rank", "Chests (S - I)")
        prefix, envname, suffix = self.get_data_by(
            prefix=prefix,
            envname=material,
            suffix=suffix
        )
        params = {
            "prefix": prefix,
            "envname": envname,
            "suffix": suffix,
            "level": level,
            "search": "Search"
        }
        other = {
            "loc": location,
            "boss": boss,
            "type": grotto_type,
            "clev": max_level,
            "rev": max_revocations,
            "glev": last_grotto_level
        }

        for key, value in other.items():
            if value is not None:
                params.setdefault(key, value)

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(self.yab_site, params=params) as response:
                if response.status != 200:
                    message = (f"Network error, report the following to the "
                               f"developer of this bot: ```py\n"
                               f"[{response.status}] - {response.message}")
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

                    for i in range(len(grottos) // self._magic):
                        segment = grottos[i * self._magic:(i+1) * self._magic]
                        # to_parse = self._create_parseable(detail)
                        args = self._parse_grotto(segment)
                        # print(len(segment), segment, len(args), args,
                        #       sep="\n", end="\n\n")
                        # args = self._parse_grotto(to_parse)

                        for i, key in enumerate(keys):
                            value = args[i:i+1]

                            if key == "Chests (S - I)":
                                value = (", ").join(map(str, args[i:i+10]))
                            else:
                                value = value[0]

                            message += (f"**{key}**: `{value}`\n")
                        message += "\n"
                    message += f"**Link**: {response.url}"

                    if len(message) > 2000:
                        # send message content to https://mystb.in/
                        # message = utils.multi_replace(message, "*`", "")
                        message = (f"`Message > 2,000 characters, refer to "
                                   f"link below`\n\n"

                                   f"{response.url}")
                        # f"{await self.hastebin(message)}")
                await ctx.send(message)
                # await self.bot.send_embed(ctx, response.url,
                #                           title="Grotto",
                #                           desc=f"[URL]({response.url})")


def setup(bot):
    bot.add_cog(DragonQuest9Cog(bot))
