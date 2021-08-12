import json
import random
from collections import OrderedDict
from typing import Dict, List, Union

import discord
import parsel
import yarl
from discord.ext import commands, menus
from jishaku.functools import executor_function

from base import custom
from checks import require_settings
from objects import Flags, Grotto


class DragonQuest9(custom.Cog):
    class Source(menus.ListPageSource):
        def __init__(self, entries: List[discord.Embed]):
            super().__init__(entries, per_page=1)

        async def format_page(self, menu: menus.Menu, entry: discord.Embed):
            return entry

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.URL = yarl.URL("https://www.yabd.org/apps/dq9/grottosearch.php")
        self.cache: Dict[yarl.URL, List[Grotto]] = {}
        self.data = {
            "chest": "IHGFEDCBAS",
            "grotto": "KJIHGFEDCBAS"
        }
        self.characteristics = {
            "gender": ["Male", "Female"],
            "hair_colour": [
                "Dark Brown",
                "Light Brown",
                "Red",
                "Pink",
                "Yellow",
                "Green",
                "Blue",
                "Purple",
                "Light Blue",
                "Grey"
            ],
            "eye_colour": [
                "Black",
                "Brown",
                "Red",
                "Yellow",
                "Green",
                "Blue",
                "Purple",
                "Grey"
            ]
        }
        self.random_character = ""

        with open("assets/names.json") as fh:
            self.characteristics["name"] = json.load(fh)

    def _create_entries(self,
                        ctx: commands.Context,
                        grottos: List[Grotto],
                        *, link: str,
                        embed: bool):
        length = len(grottos)
        ret = []
        entries = []

        for i, grotto in enumerate(grottos, start=1):
            append = OrderedDict(
                title=f"**Page #{i} ({i}/{length})**\n",
                desc=ctx.author.name
            )

            for name, payload in grotto.details.items():
                key = f"**{name.title()}**"
                append[key] = ""

                if name == "chests":
                    append[key] += "```\n"
                    items = list(payload.items())

                    for i in range(2):
                        start = i * 5
                        end = start + 5
                        spliced = (f"{k}: {v:>2}" for k, v in items[start:end])
                        append[key] += (" | ").join(spliced) + "\n"

                    append[key] += "```"
                else:
                    start = "`"
                    end = "`"

                    if name == "boss" and payload == "Greygnarl":
                        start = "||`"
                        end = "`||"
                    elif name == "special" and payload:
                        # special-case adding the indicator
                        name = append["**Name**"]
                        append["**Name**"] = f"⭐ {name}"

                        # revert current entry
                        del append[key]
                        continue
                    append[key] += f"{start}{payload}{end}"

            append["\n**Link**"] = f"<{link}>"
            entries.append(append)

        for payload in entries:
            append: Union[discord.Embed, str] = None
            title = payload.pop("title")
            desc = payload.pop("desc")

            if embed:
                payload["\n**Link**"] = f"[Link]({link})"
                fields = [custom.Field(n, v) for n, v in payload.items()]
                # image = self._generate_locations_image()
                append = custom.Embed(title=title, desc=desc, fields=fields)
            else:
                joined = ("\n").join(f"{k}: {v}" for k, v in payload.items())
                append = (f"{title}\n"
                          f"{desc}\n\n"

                          f"{joined}")

            ret.append(append)
        return ret

    def _get_paginator(self, entries: List[str]):
        source = self.Source(entries)

        return menus.MenuPages(
            source=source,
            timeout=90.0,
            clear_reactions_after=True
        )

    def _generate_random_character(self):
        return OrderedDict(
            gender=random.choice(self.characteristics["gender"]),
            body_type=random.randint(1, 5),
            hairstyle=random.randint(1, 10),
            hair_colour=random.choice(self.characteristics["hair_colour"]),
            face=random.randint(1, 10),
            skin_colour=random.randint(1, 8),
            eye_colour=random.choice(self.characteristics["eye_colour"]),
            name=random.choice(self.characteristics["name"])
        )

    @executor_function
    def _generate_grottos(self, text: str):
        grottos = []
        selector = parsel.Selector(text=text)
        grotto_divs = selector.css(".inner")

        for div in grotto_divs:
            payload = div.css("::text")
            grotto = Grotto(payload)

            grottos.append(grotto)
        return grottos

    @commands.command()
    async def resolve(self,
                      ctx: commands.Context,
                      medium: str,
                      value: Union[int, str]):
        number = letter = None
        _type = "Rank"
        medium = medium.lower()
        data = self.data.get(medium)
        message = "**{type}**: `{letter} ({number})`"

        if not data:
            return

        if isinstance(value, int) and value > -1 and value <= len(data):
            number = value
            letter = data[number - 1]
        elif isinstance(value, str):
            value = value.upper()

            if value not in data:
                return
            number = data.index(value) + 1
            letter = value

        if letter and number:
            formatted = message.format(
                type=_type,
                letter=letter,
                number=number
            )

            await ctx.send(formatted)

    @commands.command(aliases=["g"])
    @commands.check(require_settings)
    async def grotto(self,
                     ctx: commands.Context,
                     prefix: Flags.PREFIX.converter,
                     material: Flags.MATERIAL.converter,
                     suffix: Flags.SUFFIX.converter,
                     level: Flags.LEVEL.converter,
                     type: Flags.TYPE.optional,
                     location: Flags.LOCATION.optional,
                     boss: Flags.BOSS.optional,
                     max_level: Flags.MAX_LEVEL.optional,
                     max_revocations: Flags.MAX_REVOCATION.optional,
                     last_grotto_level: Flags.LAST_GROTTO_LEVEL.optional):
        link = ""
        settings = self.bot.db.settings[ctx.author.id]
        entries = []
        params = {"search": "Search"}
        command_params = [
            prefix,
            material,
            suffix,
            level,
            type,
            location,
            boss,
            max_level,
            max_revocations,
            last_grotto_level
        ]
        filtered_params = [
            param
            for param in command_params
            if param
        ]

        for param in filtered_params:
            params.update(**param.to_dict())

        URL = self.URL.with_query(params)
        link = str(URL)
        grottos = self.cache.get(URL)

        if not grottos:
            async with self.bot.session.post(URL) as response:
                text = await response.text(encoding="UTF-8")
                grottos = await self._generate_grottos(text)

                self.cache[URL] = grottos
        entries = self._create_entries(
            ctx,
            grottos,
            link=link,
            embed=settings.embed
        )
        paginator = self._get_paginator(entries)

        await paginator.start(ctx)

    @commands.command(name="random")
    async def _random(self, ctx):
        characteristics = self._generate_random_character()

        if not self.random_character:
            self.random_character = "\n".join(
                "**{name}**: {prefix}{{{key}}}".format(
                    name=key.replace("_", " ").title(),
                    prefix="Type " if isinstance(value, int) else "",
                    key=key
                )
                for key, value in characteristics.items()
            )
        content = self.random_character.format(**characteristics)

        await ctx.send(content)


def setup(bot):
    bot.add_cog(DragonQuest9(bot))
