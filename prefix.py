"""Explanation"""
from discord.ext import commands

with open("./resources/_prefix", "r") as f:
    DEFAULT = str.strip(f.read())


def get():
    return commands.when_mentioned_or(DEFAULT)


def update(prefix: str):
    DEFAULT = prefix

    with open("./resources/_prefix", "w") as f:
        f.write(f"{prefix}\n")
