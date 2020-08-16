"""Explanation"""
from discord.ext import commands
from discord.ext import flags

import emojis
import utils


class OwnerCog(commands.Cog, name="Owner Only",
               command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = True

    async def __hackclose(self):
        await super(self.bot.__class__, self.bot).close()

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

    @commands.command()
    async def clear(self, ctx):
        utils.clear_screen()
        print(self.bot.user.name, end="\n\n")

    @flags.add_flag("--force", "-f", action="store_true")
    @flags.command()
    async def close(self, ctx, **flags):
        self.bot.dispatch("close")
        await self.bot.close(forced_close=flags.get("force"))


def setup(bot):
    bot.add_cog(OwnerCog(bot))
