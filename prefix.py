"""Explanation"""
from discord.ext import commands


async def get_prefix(bot, message):
    function = commands.when_mentioned_or(bot.settings.get("prefix"))
    return function(bot, message)
