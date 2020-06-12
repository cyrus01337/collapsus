"""Explanation"""
import sqlite3
# import sys

import discord
from discord.ext import commands

import prefix
import quotes


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
        message = ""

        if isinstance(error, self.ignored):
            return print(type(error).__name__)
        elif isinstance(error, quotes.InternalQuotesError):
            message = str.capitalize(error.message)
        elif isinstance(error, sqlite3.OperationalError):
            if str(error) == "database is locked":
                message = (f"The database is locked which prevents command "
                           f"systems like `{prefix.DEFAULT}quote` to no "
                           f"longer work. Please let the developer know that "
                           f"he's an idiot and needs to close his database "
                           f"browser")
            else:
                message = error
        else:
            message = error

        try:
            await ctx.send(message)
            # prepend linebreak to improve error message readability
            print()
        except discord.Forbidden:
            pass
        finally:
            raise error


def setup(bot):
    bot.add_cog(ErrorHandlerCog(bot))
