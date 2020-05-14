"""Explanation"""
import aiohttp
from discord.ext import commands
from parsel import Selector

from constants import Owner


class TestingCog(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = True

    async def _default(self, ctx):
        await ctx.send("Working!")

    async def cog_check(self, ctx):
        return ctx.author.id == Owner.DJ.value

    @commands.group(invoke_without_subcommand=True)
    async def test(self, ctx, prefix, material, suffix, level: int,
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

        for key, value in other.items():
            if value is not None:
                params.setdefault(key, value)

        params.setdefault("search", "Search")

        async with aiohttp.ClientSession() as session:
            async with session.post(self.yab_site, params=params) as response:
                await self.bot.send_embed(ctx, title="Grotto",
                                          desc=f"[URL]({response.url})")
                selector = Selector(text=response.text)
                divs = selector.xpath('//div[@class="inner"]').getall()
                print(*divs, sep="\n\n")

    @test.group()
    async def outer(self, ctx, *args, **kwargs):
        await self._default(ctx)

    @outer.command()
    async def inner(self, ctx, *args, **kwargs):
        await self._default(ctx)


def setup(bot):
    bot.add_cog(TestingCog(bot))
