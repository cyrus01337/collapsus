from typing import List

import parsel
from discord.ext import commands, menus
from jishaku.functools import executor_function

from base import custom
from objects import Flags, Grotto


class DragonQuest9(custom.Cog):
    class Source(menus.ListPageSource):
        def __init__(self, entries):
            super().__init__(entries, per_page=1)

        async def format_page(self, menu, entry):
            return entry

    def __init__(self, bot):
        self.bot = bot

        self.URL = "https://www.yabd.org/apps/dq9/grottosearch.php"

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

    def _create_entries(self, grottos: List[Grotto], *, link: str):
        length = len(grottos)
        entries = []

        for i, grotto in enumerate(grottos, start=1):
            append = f"**Page #{i} ({i}/{length})**\n\n"

            for name, value in grotto.details:
                append += f"**{name.title()}:** `{value}`\n"

            append += (f"\n**Link:** <{link}>")
            entries.append(append)
        return entries

    def _get_paginator(self, entries: List[str]):
        source = self.Source(entries)

        return menus.MenuPages(
            source=source,
            timeout=90.0,
            clear_reactions_after=True
        )

    @commands.command(aliases=["g"])
    async def grotto(self,
                     ctx,
                     prefix: Flags.PREFIX.converter,
                     material: Flags.MATERIAL.converter,
                     suffix: Flags.SUFFIX.converter,
                     level: Flags.LEVEL.converter):
        link = ""
        entries = []
        params = {"search": "Search"}

        for param in [prefix, material, suffix, level]:
            params.update(**param.to_dict())

        async with self.bot.session.post(self.URL, params=params) as response:
            link = response.url
            text = await response.text(encoding="UTF-8")

        grottos = await self._generate_grottos(text)
        entries = self._create_entries(grottos, link=link)
        paginator = self._get_paginator(entries)

        await paginator.start(ctx)


def setup(bot):
    bot.add_cog(DragonQuest9(bot))
