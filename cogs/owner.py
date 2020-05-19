"""Explanation"""
import contextlib
import io
import json
import textwrap
import traceback
from collections.abc import Iterable

import aiohttp
from discord.ext import commands

import emojis
import utils
from constants import Owner
from constants import HEADERS


class OwnerCog(commands.Cog, name="Owner Only",
               command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.mystbin = "https://mystb.in"
        self.hidden = True
        self.cog_names = self.bot.get_cog_filenames()

    def convert(self, codeblock: str):
        for sub in ["```py\n", "\n```"]:
            codeblock = codeblock.replace(sub, "")
        indented = textwrap.indent(codeblock, "  ")

        return (f"async def function():\n"
                f"{indented}")

    def resolve_cog(self, name: str):
        name = name.lower()

        for cog in self.cog_names:
            if cog.startswith(name):
                return cog
        return None

    async def hastebin(self, message: str):
        if message.endswith("\n") is False:
            message += "\n"

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            response = await session.post(f"{self.mystbin}/documents",
                                          data=message)
            json = await response.json()
            key = json.get("key")

            return f"{self.mystbin}/{key}"

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    async def cog_before_invoke(self, ctx):
        if ctx.command.name == "close":
            await utils.react_with(ctx, emojis.THUMBS_UP)

    async def cog_after_invoke(self, ctx):
        if ctx.command_failed is False and ctx.command.name != "close":
            await utils.react_with(ctx, emojis.THUMBS_UP)
        elif ctx.command_failed:
            await utils.react_with(ctx, emojis.THUMBS_DOWN)

    async def cog_command_error(self, ctx, error):
        formatted = traceback.format_exception(type(error), error,
                                               error.__traceback__)
        tb = ("").join(formatted)
        await ctx.send(f"```py\n"
                       f"{tb}\n"
                       f"```")
        raise error

    @commands.command(aliases=["load", "unload", "reload", "r"])
    async def manipulate_cog(self, ctx, *cogs):
        manipulated = []
        prefix = "reload" if ctx.invoked_with == "r" else ctx.invoked_with
        manipulate_extension = getattr(self.bot, f"{prefix}_extension")

        for cog in cogs:
            if cog == "all" and len(manipulated) != len(self.cog_names):
                manipulated = self.cog_names
            elif cog != "all":
                resolved_name = self.resolve_cog(cog)

                if (resolved_name is not None and
                        resolved_name not in manipulated):
                    manipulated.append(resolved_name)
                    manipulate_extension(f"cogs.{resolved_name}")

        if len(manipulated) > 0:
            context = str.capitalize(f"{prefix}ed")
            cogs = (", ").join([f"`{cog}`" for cog in manipulated])
            await ctx.send(f"{context} {len(manipulated)} cog(s) - {cogs}")

    @commands.command()
    async def clear(self, ctx):
        utils.clear_screen()
        print(self.bot.user.name, end="\n\n")

    @commands.command()
    async def refresh(self, ctx, data="cogs"):
        if data == "cogs":
            self.cog_names = self.bot.get_cog_filenames()

    @commands.command(name="eval")
    async def _eval(self, ctx, *, codeblock):
        if ctx.author.id != Owner.CYRUS.value:
            return
        stdout = io.StringIO()
        env = {
            "self": self,
            "bot": self.bot,
            "ctx": ctx,
            "guild": ctx.guild,
            "author": ctx.author,
            "channel": ctx.channel,
            **globals()
        }
        source = self.convert(codeblock)
        exec(source, env)
        function = env.get("function")

        with contextlib.redirect_stdout(stdout):
            ret = await function()

        if isinstance(ret, Iterable):
            try:
                formatted = json.dumps(ret, indent=4, sort_keys=True)
            except Exception:
                pass
            else:
                ret = formatted

        await ctx.send(f"```py\n"
                       f"{ret}\n"
                       f"```")

    @commands.command()
    async def close(self, ctx):
        await self.bot.close()


def setup(bot):
    bot.add_cog(OwnerCog(bot))
