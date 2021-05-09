import traceback

from discord.ext import commands

from errors import CollapsusError


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, "original", error)

        if isinstance(error, (commands.BadArgument, CollapsusError)):
            await ctx.send(error)
        else:
            traceback.print_exception(type(error), error, error.__traceback__)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
