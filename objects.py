import enum
from collections import namedtuple
from typing import Union

from discord.ext import commands

Parameter = namedtuple("Parameter", "name value")


class Threshold:
    def __init__(self, *, min: int, max: int, hex: bool = False):
        self._hex = hex
        self.min = min
        self.max = max

    def is_hex(self):
        return self._hex


class Flags(enum.Enum):
    PREFIX = [
        "clay",
        "rock",
        "granite",
        "basalt",
        "graphite",
        "iron",
        "copper",
        "bronze",
        "steel",
        "silver",
        "gold",
        "platinum",
        "ruby",
        "emerald",
        "sapphire",
        "diamond"
    ]
    ENVNAME = [
        "cave",
        "tunnel",
        "mine",
        "crevasse",
        "marsh",
        "lair",
        "icepit",
        "lake",
        "crater",
        "path",
        "snowhall",
        "moor",
        "dungeon",
        "crypt",
        "nest",
        "ruins",
        "tundra",
        "waterway",
        "world",
        "abyss",
        "maze",
        "glacier",
        "chasm",
        "void"
    ]
    SUFFIX = [
        "joy",
        "bliss",
        "glee",
        "doubt",
        "woe",
        "dolour",
        "regret",
        "bane",
        "fear",
        "dread",
        "hurt",
        "gloom",
        "doom",
        "evil",
        "ruin",
        "death"
    ]
    LEVEL = Threshold(min=1, max=99)
    TYPE = [
        "caves",
        "ruins",
        "ice",
        "water",
        "fire"
    ]
    LOC = Threshold(min=1, max=150, hex=True)
    BOSS = [
        "equinox",
        "nemean",
        "shogum",
        "trauminator",
        "elusid",
        "sir sanguinus",
        "atlas",
        "hammibal",
        "fowleye",
        "excalipurr",
        "tyrannosaurus wrecks",
        "greygnarl"
    ]
    CLEV = Threshold(min=1, max=99)
    REV = Threshold(min=0, max=10)
    GLEV = Threshold(min=0, max=99)

    @classmethod
    def _resolve_name(cls, name: str):
        pass

    def converter(self, argument):
        argument = argument.lower()
        name = self.name.lower()
        resolved = self._resolve_name(name)

        if isinstance(self.value, list):
            if argument not in self.value:
                raise commands.BadArgument(f"{argument} is an invalid {name}")
            return Parameter(resolved, self.value.index(argument))
        elif isinstance(self.value, Threshold):
            base = 10

            if self.value.is_hex():
                base = 16
            argument = int(argument, base=base)

            if not (self.value.min <= argument <= self.value.max):
                raise commands.BadArgument(f"{argument} is an invalid {name}")
            return Parameter(resolved, argument)
        raise commands.BadArgument(f"invalid datatype passed: {argument}")
