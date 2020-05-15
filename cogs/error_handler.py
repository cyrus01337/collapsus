"""Explanation"""
# import sys

# import discord
from discord.ext import commands


class ErrorHandlerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = True
        self.ignored = (
            commands.CheckFailure,
            commands.CommandNotFound
        )

    # @commands.Cog.listener()
    # async def on_error(self, event, *args, **kwargs):
    #     error = sys.exc_info()[1]
    #     raise error

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error, *args, **kwargs):
        error = getattr(error, "original", error)

        if isinstance(error, self.ignored):
            return print(type(error).__name__)
        else:
            await ctx.send(error)
            raise error


def setup(bot):
    bot.add_cog(ErrorHandlerCog(bot))
