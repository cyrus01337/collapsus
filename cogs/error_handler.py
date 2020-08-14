"""Explanation"""
import sqlite3
import sys
import traceback

import discord
from discord.ext import commands

import database
import prefix
# import quotes
from constants import IGNORED_ERRORS


class ErrorHandlerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = True

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        error = sys.exc_info()[1]

        if isinstance(error, self.ignored):
            return
        raise error

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error, *args, **kwargs):
        error = getattr(error, "original", error)
        message = ""

        if isinstance(error, IGNORED_ERRORS):
            return print(type(error).__name__)
        elif isinstance(error, database.InternalQuotesError):
            message = str.capitalize(error.message)
        elif isinstance(error, sqlite3.OperationalError):
            if str(error) == "database is locked":
                message = (f"The database is locked which prevents command "
                           f"systems like `{ctx.prefix}quote` to no "
                           f"longer work. Please let the developer know that "
                           f"he's an idiot and needs to close his database "
                           f"browser")
            else:
                message = error
        else:
            message = error

        try:
            if not isinstance(message, str):
                formatted = traceback.format_exception(type(error), error,
                                                       error.__traceback__)
                tb = ("").join(formatted)
                message = (f"```py\n"
                           f"{tb}\n"
                           f"```")

            await ctx.send(message)
        except discord.Forbidden:
            pass
        finally:
            # prepend linebreak to improve error message readability
            print()
            raise error


def setup(bot):
    bot.add_cog(ErrorHandlerCog(bot))
