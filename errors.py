from discord.ext import commands


class CollapsusError(commands.CommandError):
    pass


class QuoteException(CollapsusError):
    pass
