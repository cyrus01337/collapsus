"""Explanation"""
from discord.ext import commands

DEFAULT = "g!"


def get():
    return commands.when_mentioned_or(DEFAULT)
