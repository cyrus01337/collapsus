"""Explanation"""
from discord.ext import commands

DEFAULT = "grotto "


def get():
    return commands.when_mentioned_or(DEFAULT)
