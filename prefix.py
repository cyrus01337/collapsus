"""Explanation"""
from discord.ext import commands


async def get_prefix(bot, message):
    return commands.when_mentioned_or(bot.settings.get("prefix"))
