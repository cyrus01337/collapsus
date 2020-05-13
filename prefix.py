"""Explanation"""
from discord.ext import commands

DEFAULT = "goo "


def get():
    return commands.when_mentioned_or(DEFAULT)
